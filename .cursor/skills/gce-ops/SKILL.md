---
name: gce-ops
description: Start, stop, and audit GCE costs for pt-vela vst-vela-01. Use when GCP billing, idle VM, emergency stop, @gce-stop, @gce-status, @gce-start, or GCE cost control.
---

# GCE ops (judgment)

**Run steps:** `.cursor/commands/gce-stop`, `gce-status`, `gce-start`, `gce-run`, `gce-jupyter`.

**Script:** `scripts/gce_vela/remote.sh` (`billing-status`, `start`, `stop`, `downsize`).

## IDs (do not swap)

| Name | Value |
| :--- | :--- |
| Project | `pt-vela` |
| VM | `vst-vela-01` |
| Zone | `europe-west4-a` |
| Bucket | `pt-vela-gce` |
| Default machine | `n1-standard-4`, **no GPU** |
| Budget alert | `pt-vela` (EUR 10/month; was misnamed `hailo`) |
| Kill switch | `@gce-budget-kill` + `scripts/gce_vela/budget_kill_switch/` |

CLI cheat sheet (if synced): `notes/gcp-setup-pt-vela.md`.

## Agent role

**Operator:** run `remote.sh` from Mac via Shell. Do not paste `gcloud` for the user unless SSH or `gcloud` is unavailable on the agent shell.

**Cost gate:** after `@gce-run` or `@gce-jupyter`, run `@gce-stop` unless the user explicitly keeps the VM running.

## Budget name "hailo" (resolved)

The Console budget was **named** `hailo`; that is only a label, not a GCP service. Renamed to **`pt-vela`**, scoped to project `416044791753`. Charges were **Compute Engine** from `vst-vela-01` left RUNNING.

## Auto-stop at EUR 10

GCP budgets **alert only** unless wired to Pub/Sub + automation.

| Layer | What |
| :--- | :--- |
| Email alerts | 50% / 90% / 100% thresholds (already set) |
| Kill switch | Cloud Function `pt-vela-budget-stop-vm` stops `vst-vela-01` when `costAmount > budgetAmount` |
| Setup | `@gce-budget-kill` or `scripts/gce_vela/budget_kill_switch/setup.sh` |

**Limits:** Pub/Sub budget messages can lag billing by hours. Use `@gce-stop` after every session; kill switch is a safety net.

## What went wrong on manual stop (2026-06-12)

GCP operation log (`gcloud compute operations list`):

| Time (PDT) | Action | Result |
| :--- | :--- | :--- |
| 2026-06-12 08:57 | **stop** | Success |
| 2026-06-12 09:13 | **stop** | Success (redundant) |
| 2026-06-12 09:19 | **start** | VM restarted |
| 2026-06-13 | (none) | VM ran all day |
| 2026-06-14 04:10 | **stop** | Emergency stop |

**Root cause:** stop on Jun 12 worked, but the VM was **started again 6 minutes later** (likely `@gce-jupyter` step 0: "if TERMINATED, start"). Closing Jupyter or SSH tunnels does **not** stop the VM. No stop ran on Jun 13.

## Hailo vs Himax vs Ethos-U

| Name | What it is | VST? |
| :--- | :--- | :--- |
| **Hailo** | Edge AI chip vendor (Hailo-8). Separate GCP repos use GPU VMs for Hailo Dataflow Compiler. | No |
| **Himax** | GV2 SoC vendor; `himax_vela.ini` for VELA compile | Yes |
| **Ethos-U** | ARM NPU on GV2; `ethos-u-vela --accelerator-config ethos-u55-64` | Yes |

`pt-vela` on this account has only `vst-vela-01`. No Hailo GCP project here.

## Why idle VMs cost money

| State | Billed |
| :--- | :--- |
| RUNNING | vCPU, RAM, GPU (if attached), mostly hourly |
| TERMINATED | Boot disk (~100 GB), GCS bucket; compute not billed |
| Forgotten Jupyter / closed terminals | VM stays RUNNING |

## Machine escalation (active work only)

1. Default: `n1-standard-4`, CPU only
2. INT8 export OOM: `n1-standard-8`
3. Still OOM: `n1-highmem-8`
4. After run: `@gce-stop`, then `remote.sh downsize` back to `n1-standard-4`

Do not attach T4 for VELA-only path (training stays Colab). Future `gcloud compute instances create` must omit `--accelerator`.

## Escalation

| Issue | Action |
| :--- | :--- |
| VM RUNNING while idle | `@gce-stop` |
| Mystery spend | `@gce-status`; Console Billing → SKU breakdown |
| GPU attached | Stop VM; recreate without accelerator |
| Budget alerts | `pt-vela` budget; `@gce-budget-kill` for auto-stop safety net |

## Out of scope

- Colab training (`@train-colab-vela`)
- Hailo edge deployment (`marcory-hub/hailo_gcp`)
- Editing `notebooks/*.ipynb` unless user says apply
