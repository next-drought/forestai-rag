-- Run as postgres after 001_schema.sql on Cloud SQL. Local docker uses postgres directly and skips this.
GRANT USAGE ON SCHEMA public TO rag_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON sources, chunks TO rag_app;
GRANT USAGE, SELECT ON SEQUENCE chunks_chunk_id_seq TO rag_app;
