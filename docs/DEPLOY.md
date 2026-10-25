# Deploy

Target: Firebase project `forestai-platform` (https://forestai-platform.web.app).

```
Browser (Firebase Auth) --ID token--> forestai-platform.web.app/api/**
   --Hosting rewrite--> Cloud Run "forestai-rag" (verifies token) --> Vertex AI Gemini
                                                                 --> Cloud SQL Postgres 16 (pgvector + PostGIS)
Cloud Run job "forestai-rag-ingest" --> Cloud SQL
```

## Steps
1. `./deploy/setup_gcp.sh` (one time): APIs, Artifact Registry, Cloud SQL, secret, service account.
2. Apply `sql/001_schema.sql` to the Cloud SQL database and grant `rag_app` access to the tables.
3. `./deploy/deploy.sh`: builds the image and deploys the service and the ingest job.
4. Load documents: bake them into the image or mount a GCS bucket, then
   `gcloud run jobs execute forestai-rag-ingest --region us-central1`.
5. Frontend: add the rewrite below to `forestai-platform-frontend/firebase.json`, **before** the `**` SPA rewrite,
   only after the Cloud Run service exists (Hosting deploys fail if the target service is missing).

```json
{ "source": "/api/**", "run": { "serviceId": "forestai-rag", "region": "us-central1" } }
```

Frontend call:
```ts
const token = await auth.currentUser!.getIdToken();
const res = await fetch("/api/query", {
  method: "POST",
  headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
  body: JSON.stringify({ question }),
});
const { answer, sources } = await res.json();
```

## CI
`.github/workflows/deploy.yml` runs tests on PRs and deploys on `main`. Needs Workload Identity Federation;
set repo secrets `GCP_WORKLOAD_IDENTITY_PROVIDER` and `GCP_DEPLOY_SERVICE_ACCOUNT` (roles: run.admin,
cloudbuild.builds.editor, artifactregistry.writer, iam.serviceAccountUser on the runtime SA).

## Notes
- Hosting rewrites time out at 60 s; keep `/api/query` under that or call the Cloud Run URL directly (CORS is configured).
- `db-g1-small` is the cheapest tier that fits; move to a larger tier or AlloyDB if latency or corpus size requires.
