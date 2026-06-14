#!/usr/bin/env bash
# Mac-side GCE remote runner. Agent calls this to SSH, stream output, and save local logs.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PROJECT_ID="pt-vela"
VM="vst-vela-01"
ZONE="europe-west4-a"
BUCKET="pt-vela-gce"
DEFAULT_MACHINE_TYPE="n1-standard-4"
VM_WORKDIR="~/vst"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_ROOT="$SCRIPT_DIR/outputs"
RUN_ID="$(date -u +%Y-%m-%dT%H%M%SZ)"
LOG_DIR="$OUTPUT_ROOT/$RUN_ID"
LOG_FILE="$LOG_DIR/remote.log"

mkdir -p "$LOG_DIR"

log_local() {
  echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG_FILE"
}

vm_ssh() {
  gcloud compute ssh "$VM" --zone="$ZONE" -- "$@"
}

vm_status_field() {
  gcloud compute instances describe "$VM" --zone="$ZONE" --format="get($1)"
}

usage() {
  cat <<'EOF'
Usage: remote.sh <command> [args]

VM lifecycle (Mac gcloud; saves cost):
  billing-status    Status, machine type, accelerators, disk, bucket size
  start             Start VM and wait until RUNNING
  stop              Stop VM and verify TERMINATED
  downsize          Stop if needed; set machine type to n1-standard-4

Pipeline (requires RUNNING VM):
  status            billing-status + pipeline health (venv, inputs, cv2/tf)
  pipeline-status   venv + inputs + cv2/tf versions on VM
  sync              Push vm_run.py (+ optional notebook) to VM
  run <step>        Run one vm_run.py step (streams to terminal + local log)
  run-resume        Skip extract/calibrate; run export pipeline
  run-all           Full pipeline (long; export ~10-20 min)
  tail [n]          Last n lines of VM agent_run.log (default 80)
  pull-log          Copy full VM agent_run.log into outputs/
  push-notebook     scp GCE notebook to VM

Steps for `run`: preflight extract pins calibrate ultralytics export
                  vela-install vela size upload
EOF
}

cmd_billing_status() {
  log_local "billing-status: project=$PROJECT_ID vm=$VM zone=$ZONE"
  local vm_state machine_type accelerators disk_gb nat_ip
  vm_state="$(vm_status_field status)"
  machine_type="$(vm_status_field machineType)"
  machine_type="${machine_type##*/}"
  accelerators="$(vm_status_field guestAccelerators)"
  disk_gb="$(vm_status_field disks[0].diskSizeGb)"
  nat_ip="$(gcloud compute instances describe "$VM" --zone="$ZONE" \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null || true)"

  echo "project: $PROJECT_ID"
  echo "vm: $VM"
  echo "zone: $ZONE"
  echo "status: $vm_state"
  echo "machine_type: $machine_type"
  if [[ -z "$accelerators" ]]; then
    echo "accelerators: none"
  else
    echo "accelerators: $accelerators"
  fi
  echo "boot_disk_gb: ${disk_gb:-unknown}"
  echo "external_ip: ${nat_ip:-none}"
  if [[ "$vm_state" == "RUNNING" ]]; then
    echo "cost_note: RUNNING instances bill vCPU/RAM hourly; GPU if attached"
  else
    echo "cost_note: compute not billed when TERMINATED; disk and GCS still bill"
  fi

  echo "--- disks ---"
  gcloud compute disks list --filter="name=$VM" --format="table(name,zone,sizeGb,status)" 2>/dev/null \
    || echo "(disk list unavailable)"

  echo "--- bucket ---"
  if command -v gsutil >/dev/null 2>&1; then
    gsutil du -sh "gs://${BUCKET}/" 2>/dev/null || echo "gs://${BUCKET}/ (unavailable)"
    gsutil ls "gs://${BUCKET}/" 2>/dev/null || true
  else
    echo "gsutil not installed"
  fi
  log_local "billing-status done"
}

cmd_stop() {
  log_local "stop: $VM ($ZONE)"
  local vm_state
  vm_state="$(vm_status_field status)"
  if [[ "$vm_state" == "TERMINATED" ]]; then
    echo "already TERMINATED"
  else
    gcloud compute instances stop "$VM" --zone="$ZONE"
  fi
  vm_state="$(vm_status_field status)"
  echo "status: $vm_state"
  if [[ "$vm_state" != "TERMINATED" ]]; then
    echo "ERROR: expected TERMINATED"
    exit 1
  fi
  log_local "stop done"
}

cmd_start() {
  log_local "start: $VM ($ZONE)"
  local vm_state
  vm_state="$(vm_status_field status)"
  if [[ "$vm_state" == "RUNNING" ]]; then
    echo "already RUNNING"
  else
    gcloud compute instances start "$VM" --zone="$ZONE"
    echo "waiting for RUNNING..."
    for _ in $(seq 1 36); do
      vm_state="$(vm_status_field status)"
      if [[ "$vm_state" == "RUNNING" ]]; then
        break
      fi
      sleep 5
    done
  fi
  vm_state="$(vm_status_field status)"
  echo "status: $vm_state"
  if [[ "$vm_state" != "RUNNING" ]]; then
    echo "ERROR: VM did not reach RUNNING within timeout"
    exit 1
  fi
  echo "reminder: run remote.sh stop or @gce-stop when work is done"
  log_local "start done"
}

cmd_downsize() {
  log_local "downsize: target=$DEFAULT_MACHINE_TYPE"
  local vm_state machine_type
  vm_state="$(vm_status_field status)"
  if [[ "$vm_state" == "RUNNING" ]]; then
    gcloud compute instances stop "$VM" --zone="$ZONE"
    vm_state="$(vm_status_field status)"
  fi
  if [[ "$vm_state" != "TERMINATED" ]]; then
    echo "ERROR: VM must be TERMINATED before resize (status=$vm_state)"
    exit 1
  fi
  machine_type="$(vm_status_field machineType)"
  machine_type="${machine_type##*/}"
  if [[ "$machine_type" == "$DEFAULT_MACHINE_TYPE" ]]; then
    echo "already $DEFAULT_MACHINE_TYPE"
  else
    gcloud compute instances set-machine-type "$VM" \
      --zone="$ZONE" \
      --machine-type="$DEFAULT_MACHINE_TYPE"
    echo "resized: $machine_type -> $DEFAULT_MACHINE_TYPE"
  fi
  cmd_billing_status
  log_local "downsize done"
}

cmd_pipeline_status() {
  log_local "pipeline-status: $VM ($ZONE)"
  local vm_state
  vm_state="$(vm_status_field status)"
  if [[ "$vm_state" != "RUNNING" ]]; then
    echo "ERROR: VM is $vm_state; run remote.sh start first"
    exit 1
  fi
  vm_ssh "bash -lc '
    set -e
    echo VM: \$(hostname)
    echo uptime: \$(uptime -p 2>/dev/null || uptime)
    test -d ~/vst/.venv || { echo ERROR: missing ~/vst/.venv; exit 1; }
    source ~/vst/.venv/bin/activate
    cd ~/vst
    echo python: \$(which python)
    python --version
    ls -lh best.pt dataset.zip 2>/dev/null || echo WARN: inputs missing
    python -c \"import cv2, tensorflow as tf; print(\\\"cv2\\\", cv2.__version__, \\\"tf\\\", tf.__version__)\" 2>&1 || echo WARN: import failed
    pgrep -af jupyter-lab || echo Jupyter: not running
  '" | tee -a "$LOG_FILE"
  log_local "pipeline-status done. local log: $LOG_FILE"
}

cmd_status() {
  cmd_billing_status | tee -a "$LOG_FILE"
  echo "--- pipeline ---"
  local vm_state
  vm_state="$(vm_status_field status)"
  if [[ "$vm_state" == "RUNNING" ]]; then
    cmd_pipeline_status
  else
    echo "pipeline check skipped (VM $vm_state)"
    log_local "status done (billing only)"
  fi
}

cmd_sync() {
  log_local "sync vm_run.py -> VM"
  gcloud compute scp "$SCRIPT_DIR/vm_run.py" "$VM:$VM_WORKDIR/vm_run.py" --zone="$ZONE"
  vm_ssh "mkdir -p ~/vst/logs && chmod +x ~/vst/vm_run.py 2>/dev/null || true"
  log_local "sync done"
}

cmd_run() {
  local step="${1:?step required}"
  local vm_state
  vm_state="$(vm_status_field status)"
  if [[ "$vm_state" != "RUNNING" ]]; then
    echo "ERROR: VM is $vm_state; run remote.sh start first"
    exit 1
  fi
  cmd_sync
  log_local "run step=$step (streaming...)"
  vm_ssh "bash -lc '
    set -e
    set -o pipefail
    source ~/vst/.venv/bin/activate
    cd ~/vst
    python vm_run.py \"$step\" 2>&1 | tee -a ~/vst/logs/agent_run.log
  '" | tee -a "$LOG_FILE"
  log_local "step=$step finished. local log: $LOG_FILE"
}

cmd_tail() {
  local lines="${1:-80}"
  vm_ssh "tail -n $lines ~/vst/logs/agent_run.log 2>/dev/null || echo '(no VM log yet)'" | tee -a "$LOG_FILE"
}

cmd_pull_log() {
  log_local "pulling VM log"
  gcloud compute scp "$VM:~/vst/logs/agent_run.log" "$LOG_DIR/vm_agent_run.log" --zone="$ZONE" 2>/dev/null \
    || vm_ssh "cat ~/vst/logs/agent_run.log" > "$LOG_DIR/vm_agent_run.log" 2>/dev/null \
    || echo "(no VM log)" > "$LOG_DIR/vm_agent_run.log"
  log_local "saved: $LOG_DIR/vm_agent_run.log"
  tail -40 "$LOG_DIR/vm_agent_run.log"
}

cmd_push_notebook() {
  local nb="$REPO_ROOT/notebooks/YOLO_pt_to_vela_2026_02_24_gce.ipynb"
  test -f "$nb" || { echo "missing $nb"; exit 1; }
  log_local "push notebook"
  gcloud compute scp "$nb" "$VM:$VM_WORKDIR/YOLO_pt_to_vela_2026_02_24_gce.ipynb" --zone="$ZONE"
  log_local "notebook on VM"
}

main() {
  gcloud config set project "$PROJECT_ID" >/dev/null
  local cmd="${1:-status}"
  shift || true
  case "$cmd" in
    billing-status) cmd_billing_status ;;
    start) cmd_start ;;
    stop) cmd_stop ;;
    downsize) cmd_downsize ;;
    status) cmd_status ;;
    pipeline-status) cmd_pipeline_status ;;
    sync) cmd_sync ;;
    run) cmd_run "$@" ;;
    run-resume) cmd_run resume ;;
    run-all) cmd_run all ;;
    tail) cmd_tail "${1:-80}" ;;
    pull-log) cmd_pull_log ;;
    push-notebook) cmd_push_notebook ;;
    -h|--help|help) usage ;;
    *) echo "Unknown command: $cmd"; usage; exit 1 ;;
  esac
}

main "$@"
