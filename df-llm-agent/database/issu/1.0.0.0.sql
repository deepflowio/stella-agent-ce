
-- 任何issu最后都需要执行该sql，且version 和文件名一致
UPDATE db_version SET version='1.0.0.0', updated_at= now();