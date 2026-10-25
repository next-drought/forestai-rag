#!/usr/bin/env bash
# One-time GCP setup for forestai-rag in the production Firebase project. Review before running.
set -euo pipefail
PROJECT=forestai-platform
REGION=us-central1
INSTANCE=forestai-rag-db
DB=forestai_rag
SA=forestai-rag@${PROJECT}.iam.gserviceaccount.com

gcloud config set project "$PROJECT"
gcloud services enable run.googleapis.com sqladmin.googleapis.com aiplatform.googleapis.com \
  secretmanager.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

gcloud artifacts repositories create forestai --repository-format=docker --location="$REGION" || true

gcloud sql instances create "$INSTANCE" --database-version=POSTGRES_16 \
  --edition=ENTERPRISE --tier=db-g1-small --region="$REGION" --storage-auto-increase
gcloud sql databases create "$DB" --instance="$INSTANCE"
DB_PASS=$(openssl rand -base64 24)
gcloud sql users create rag_app --instance="$INSTANCE" --password="$DB_PASS"

CONN=$(gcloud sql instances describe "$INSTANCE" --format='value(connectionName)')
printf 'postgresql://rag_app:%s@/%s?host=/cloudsql/%s' "$DB_PASS" "$DB" "$CONN" |
  gcloud secrets create forestai-rag-database-url --data-file=-

gcloud iam service-accounts create forestai-rag || true
for role in roles/aiplatform.user roles/cloudsql.client roles/secretmanager.secretAccessor roles/firebaseauth.viewer; do
  gcloud projects add-iam-policy-binding "$PROJECT" --member="serviceAccount:$SA" --role="$role" --condition=None
done

echo "Next: connect with 'gcloud sql connect $INSTANCE --user=postgres', run sql/001_schema.sql"
echo "(it creates the vector and postgis extensions), then grant rag_app access to the tables."
