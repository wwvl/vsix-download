-- 删除触发器（如果存在）
DROP TRIGGER IF EXISTS update_extensions_updated_at ON extensions;

-- 删除函数（如果存在）
DROP FUNCTION IF EXISTS update_updated_at_column();

-- 删除表（如果存在）
DROP TABLE IF EXISTS extensions CASCADE;
