#!/usr/bin/env bash
# Build and deploy the API service and the ingest job to Cloud Run.
set -euo pipefail
PROJECT=forestai-platform
REGION=us-central1
CONN=${PROJECT}:${REGION}:forestai-rag-db
SA=forestai-rag@${PROJECT}.iam.gserviceaccount.com
IMAGE=${REGION}-docker.pkg.dev/${PROJECT}/forestai/forestai-rag:${TAG:-$(git rev-parse --short HEAD 2>/dev/null || date +%s)}
ENV_VARS=GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=${PROJECT},GOOGLE_CLOUD_LOCATION=${REGION}

gcloud builds submit --project "$PROJECT" --tag "$IMAGE" .

# Public at the IAM layer so Firebase Hosting can reach it; the app enforces Firebase Auth.
gcloud run deploy forestai-rag --project "$PROJECT" --region "$REGION" --image "$IMAGE" \
  --service-account "$SA" --add-cloudsql-instances "$CONN" \
  --set-env-vars "$ENV_VARS" --set-secrets DATABASE_URL=forestai-rag-database-url:latest \
  --allow-unauthenticated --min-instances 0 --max-instances 5 --memory 1Gi --timeout 60

gcloud run jobs deploy forestai-rag-ingest --project "$PROJECT" --region "$REGION" --image "$IMAGE" \
  --service-account "$SA" --set-cloudsql-instances "$CONN" \
  --set-env-vars "$ENV_VARS" --set-secrets DATABASE_URL=forestai-rag-database-url:latest \
  --command python --args scripts/run_ingest.py,data/raw --task-timeout 3600
