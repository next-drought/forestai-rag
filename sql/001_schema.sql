CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS sources (
  source_id    TEXT PRIMARY KEY,
  title        TEXT NOT NULL,
  url          TEXT,
  license      TEXT,
  retrieved_on DATE,
  checksum     TEXT,
  version      TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
  chunk_id     BIGSERIAL PRIMARY KEY,
  source_id    TEXT REFERENCES sources(source_id) ON DELETE CASCADE,
  parent_id    BIGINT,
  section      TEXT,
  page         INT,
  text         TEXT NOT NULL,
  metadata     JSONB NOT NULL DEFAULT '{}',   -- species, region, year, data_type, access_level
  embed_model  TEXT NOT NULL,
  embedding    vector(768),
  tsv          tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
  geom         geometry(Geometry, 4326)
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING gin (tsv);
CREATE INDEX IF NOT EXISTS chunks_meta_idx ON chunks USING gin (metadata);
CREATE INDEX IF NOT EXISTS chunks_geom_idx ON chunks USING gist (geom);
