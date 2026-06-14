"""Stop vst-vela-01 when monthly budget cost exceeds budget amount (Pub/Sub trigger)."""
import base64
import json
import os

from googleapiclient import discovery

PROJECT_ID = os.environ.get("GCP_PROJECT", "pt-vela")
ZONE = os.environ.get("GCP_ZONE", "europe-west4-a")
VM_NAME = os.environ.get("VM_NAME", "vst-vela-01")


def budget_stop_vm(event, context):
    """Cloud Function entry point for programmatic budget notifications."""
    payload = base64.b64decode(event["data"]).decode("utf-8")
    message = json.loads(payload)
    cost_amount = float(message.get("costAmount", 0))
    budget_amount = float(message.get("budgetAmount", 0))
    budget_name = message.get("budgetDisplayName", "unknown")

    if cost_amount <= budget_amount:
        print(f"No action: cost {cost_amount} <= budget {budget_amount} ({budget_name})")
        return

    compute = discovery.build("compute", "v1", cache_discovery=False)
    instance = (
        compute.instances()
        .get(project=PROJECT_ID, zone=ZONE, instance=VM_NAME)
        .execute()
    )
    status = instance.get("status")
    if status != "RUNNING":
        print(f"No action: {VM_NAME} status is {status}")
        return

    compute.instances().stop(project=PROJECT_ID, zone=ZONE, instance=VM_NAME).execute()
    print(f"Stopped {VM_NAME}: cost {cost_amount} > budget {budget_amount} ({budget_name})")
