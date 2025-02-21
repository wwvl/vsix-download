-- 删除触发器（如果存在）
DROP TRIGGER IF EXISTS update_extension_search_vectors ON extensions;

-- 删除函数（如果存在）
DROP FUNCTION IF EXISTS update_search_vectors();

-- 删除索引（如果存在）
DROP INDEX IF EXISTS idx_extension_full_name;
DROP INDEX IF EXISTS idx_last_updated;
DROP INDEX IF EXISTS idx_display_name;
DROP INDEX IF EXISTS idx_categories;
DROP INDEX IF EXISTS idx_tags;
DROP INDEX IF EXISTS idx_extension_search_text;
DROP INDEX IF EXISTS idx_extension_search_en;
DROP INDEX IF EXISTS idx_extension_search_zh;
DROP INDEX IF EXISTS idx_extension_search;

-- 删除表（如果存在）
DROP TABLE IF EXISTS extensions;

-- 删除之前创建的搜索配置（如果存在）
DROP TEXT SEARCH CONFIGURATION IF EXISTS zh;

-- 注意：不删除扩展，因为其他表可能也在使用
-- 如果确实需要删除扩展，请取消下面的注释
-- DROP EXTENSION IF EXISTS pg_trgm;
-- DROP EXTENSION IF EXISTS unaccent;
