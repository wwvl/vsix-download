-- 创建表和索引的 SQL 语句
CREATE TABLE extensions (
    extension_name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    short_description TEXT,
    latest_version TEXT NOT NULL,
    last_updated TIMESTAMPTZ NOT NULL,
    version_history JSONB NOT NULL,
    categories TEXT[] NOT NULL DEFAULT '{}',
    tags TEXT[] NOT NULL DEFAULT '{}',
    download_url TEXT NOT NULL,
    marketplace_url TEXT NOT NULL
);

