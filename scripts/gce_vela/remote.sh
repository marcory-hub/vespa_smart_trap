#!/usr/bin/env bash
# Mac-side GCE remote runner. Agent calls this to SSH, stream output, and save local logs.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VM="vst-vela-01"
ZONE="europe-west4-a"
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

usage() {
  cat <<'EOF'
Usage: remote.sh <command> [args]

Commands (agent runs these; user does not need to paste output):
  status              VM + venv + inputs + cv2/tf versions
  sync                Push vm_run.py (+ optional notebook) to VM
  run <step>          Run one vm_run.py step (streams to terminal + local log)
  run-resume          Skip extract/calibrate; run export pipeline
  run-all             Full pipeline (long; export ~10-20 min)
  tail [n]            Last n lines of VM agent_run.log (default 80)
  pull-log            Copy full VM agent_run.log into outputs/
  push-notebook       scp GCE notebook to VM

Steps for `run`: preflight extract pins calibrate ultralytics export
                  vela-install vela size upload
EOF
}

cmd_status() {
  log_local "status: $VM ($ZONE)"
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
  log_local "local log: $LOG_FILE"
}

cmd_sync() {
  log_local "sync vm_run.py -> VM"
  gcloud compute scp "$SCRIPT_DIR/vm_run.py" "$VM:$VM_WORKDIR/vm_run.py" --zone="$ZONE"
  vm_ssh "mkdir -p ~/vst/logs && chmod +x ~/vst/vm_run.py 2>/dev/null || true"
  log_local "sync done"
}

cmd_run() {
  local step="${1:?step required}"
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
  local cmd="${1:-status}"
  shift || true
  case "$cmd" in
    status) cmd_status ;;
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
