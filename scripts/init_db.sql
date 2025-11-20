-- 初始化数据库脚本

-- 创建数据库
CREATE DATABASE IF NOT EXISTS wecom_db;

-- 切换到数据库
\c wecom_db;

-- 启用pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 验证扩展
SELECT * FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp');

