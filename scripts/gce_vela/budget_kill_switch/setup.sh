#!/usr/bin/env bash
# One-time setup: Pub/Sub budget notifications -> Cloud Function stops vst-vela-01 at €10.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ID="pt-vela"
PROJECT_NUMBER="416044791753"
BILLING_ACCOUNT="01C6E6-3979EC-357FD7"
BUDGET_ID="41e9b2e3-229a-4663-bb8c-40db5d00bbe9"
TOPIC="pt-vela-budget-alerts"
FUNCTION_NAME="pt-vela-budget-stop-vm"
REGION="europe-west4"
ZONE="europe-west4-a"
VM_NAME="vst-vela-01"
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud config set project "$PROJECT_ID" >/dev/null

echo "Enabling APIs..."
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  eventarc.googleapis.com \
  run.googleapis.com \
  pubsub.googleapis.com \
  billingbudgets.googleapis.com \
  --quiet

if ! gcloud pubsub topics describe "$TOPIC" >/dev/null 2>&1; then
  gcloud pubsub topics create "$TOPIC"
  echo "Created topic: $TOPIC"
else
  echo "Topic exists: $TOPIC"
fi

echo "Deploying Cloud Function (Pub/Sub trigger)..."
gcloud functions deploy "$FUNCTION_NAME" \
  --gen2 \
  --region="$REGION" \
  --runtime=python311 \
  --source="$SCRIPT_DIR" \
  --entry-point=budget_stop_vm \
  --trigger-topic="$TOPIC" \
  --set-env-vars="GCP_PROJECT=${PROJECT_ID},GCP_ZONE=${ZONE},VM_NAME=${VM_NAME}" \
  --service-account="$RUNTIME_SA" \
  --quiet

echo "Granting compute.instanceAdmin.v1 to function service account..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/compute.instanceAdmin.v1" \
  --condition=None \
  --quiet >/dev/null

echo "Linking budget to Pub/Sub (programmatic notifications)..."
gcloud billing budgets update "billingAccounts/${BILLING_ACCOUNT}/budgets/${BUDGET_ID}" \
  --notifications-rule-pubsub-topic="projects/${PROJECT_ID}/topics/${TOPIC}" \
  --format="yaml(displayName,notificationsRule)"

echo ""
echo "Done. When monthly spend exceeds EUR 10, budget messages trigger stop of ${VM_NAME}."
echo "Note: Pub/Sub notifications lag billing by up to several hours; not instant."
echo "Verify: gcloud billing budgets describe billingAccounts/${BILLING_ACCOUNT}/budgets/${BUDGET_ID}"
