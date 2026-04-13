import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import mysql.connector
from app.config.config import DATABASE_CONFIG

def init_mysql():
    print("开始初始化MySQL数据库...")
    
    # 连接到MySQL服务器
    try:
        # 先连接到默认的mysql数据库
        conn = mysql.connector.connect(
            host=DATABASE_CONFIG['mysql']['host'],
            port=DATABASE_CONFIG['mysql']['port'],
            user=DATABASE_CONFIG['mysql']['user'],
            password=DATABASE_CONFIG['mysql']['password'],
            database='mysql'
        )
        cursor = conn.cursor()
        
        # 创建数据库
        db_name = DATABASE_CONFIG['mysql']['database']
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"数据库 {db_name} 创建成功")
        
        # 切换到新创建的数据库
        cursor.execute(f"USE {db_name}")
        
        # 创建科室表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS department (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        print("科室表创建成功")
        
        # 创建医生表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            department_id INT,
            title VARCHAR(100),
            description TEXT,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES department(id)
        )
        """)
        print("医生表创建成功")
        
        # 创建预约表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointment (
            id INT PRIMARY KEY AUTO_INCREMENT,
            patient_name VARCHAR(100) NOT NULL,
            patient_id VARCHAR(20) NOT NULL,
            department_id INT,
            doctor_id INT,
            appointment_date DATE NOT NULL,
            appointment_time VARCHAR(20) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES department(id),
            FOREIGN KEY (doctor_id) REFERENCES doctor(id)
        )
        """)
        print("预约表创建成功")
        
        # 插入科室数据
        departments = [
            ("内科", "内科是医院的基础科室，负责诊断和治疗内脏疾病"),
            ("外科", "外科主要负责需要手术治疗的疾病"),
            ("儿科", "儿科专门负责儿童的医疗保健"),
            ("妇产科", "妇产科负责女性生殖系统疾病和孕产相关服务"),
            ("神经内科", "神经内科负责神经系统疾病的诊断和治疗")
        ]
        cursor.executemany("INSERT INTO department (name, description) VALUES (%s, %s) ON DUPLICATE KEY UPDATE description = VALUES(description)", departments)
        print("科室数据插入成功")
        
        # 提交事务
        conn.commit()
        print("MySQL数据库初始化完成")
        
    except Exception as e:
        print(f"MySQL初始化失败: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_mysql()
