# Postgres 16 with pgvector and PostGIS, matching the Cloud SQL extensions.
# pgvector/pgvector is multi-arch (native on Apple silicon) and ships the PGDG apt repo.
FROM pgvector/pgvector:pg16
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-16-postgis-3 \
    && rm -rf /var/lib/apt/lists/*
