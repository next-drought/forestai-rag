-- Run as postgres after 001_schema.sql. Skipped where rag_app doesn't exist (local docker uses postgres).
DO $$
BEGIN
  IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'rag_app') THEN
    GRANT USAGE ON SCHEMA public TO rag_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON sources, chunks TO rag_app;
    GRANT USAGE, SELECT ON SEQUENCE chunks_chunk_id_seq TO rag_app;
  END IF;
END $$;
