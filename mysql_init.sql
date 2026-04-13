-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS guiguxiaozhi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE guiguxiaozhi;

-- 创建预约挂号表
CREATE TABLE IF NOT EXISTS appointment (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL COMMENT '患者姓名',
    id_card VARCHAR(20) NOT NULL COMMENT '身份证号',
    department VARCHAR(100) NOT NULL COMMENT '预约科室',
    date VARCHAR(20) NOT NULL COMMENT '预约日期',
    time VARCHAR(10) NOT NULL COMMENT '预约时间',
    doctor_name VARCHAR(50) COMMENT '医生姓名',
    UNIQUE KEY uk_appointment (username, id_card, department, date, time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预约挂号表';