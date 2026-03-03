-- 为 user 表添加 email 和 name 列
-- 执行前请确保数据库名正确（根据 application-dev.yml 中的配置，数据库名为 material_database）

USE material_database;

-- 检查并添加 email 列（如果不存在）
-- 注意：MySQL 不支持 IF NOT EXISTS for columns，如果列已存在会报错，可以忽略
ALTER TABLE `user` 
ADD COLUMN `email` VARCHAR(255) NULL COMMENT '邮箱' 
AFTER `password`;

-- 检查并添加 name 列（如果不存在）
-- 注意：如果列已存在会报错，可以忽略
ALTER TABLE `user` 
ADD COLUMN `name` VARCHAR(100) NULL COMMENT '用户名/真实姓名' 
AFTER `email`;

-- 如果需要验证列是否添加成功，可以执行：
-- DESCRIBE `user`;

