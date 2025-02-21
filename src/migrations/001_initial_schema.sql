-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- 创建表和索引的 SQL 语句
CREATE TABLE extensions (
    id BIGSERIAL PRIMARY KEY,
    extension_id TEXT NOT NULL UNIQUE,
    extension_name TEXT NOT NULL,
    extension_full_name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    short_description TEXT,
    latest_version TEXT NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL,
    version_history JSONB NOT NULL,
    categories JSONB,
    tags JSONB,
    download_url TEXT NOT NULL,
    filename TEXT NOT NULL,
    marketplace_url TEXT NOT NULL,
    search_text TEXT GENERATED ALWAYS AS (
        display_name || ' ' ||
        COALESCE(short_description, '') || ' ' ||
        extension_name
    ) STORED,
    search_vector_en tsvector GENERATED ALWAYS AS (
        to_tsvector('english',
            COALESCE(extension_name, '') || ' ' ||
            COALESCE(display_name, '') || ' ' ||
            COALESCE(short_description, '')
        )
    ) STORED
);

