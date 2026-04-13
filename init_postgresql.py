import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from app.config.config import DATABASE_CONFIG

def init_postgresql():
    print("开始初始化PostgreSQL数据库...")
    
    # 连接到PostgreSQL服务器
    try:
        # 先连接到默认的postgres数据库
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['postgresql']['host'],
            port=DATABASE_CONFIG['postgresql']['port'],
            user=DATABASE_CONFIG['postgresql']['user'],
            password=DATABASE_CONFIG['postgresql']['password'],
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 创建数据库
        db_name = DATABASE_CONFIG['postgresql']['database']
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"数据库 {db_name} 创建成功")
        else:
            print(f"数据库 {db_name} 已存在")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        # 连接到新创建的数据库
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['postgresql']['host'],
            port=DATABASE_CONFIG['postgresql']['port'],
            user=DATABASE_CONFIG['postgresql']['user'],
            password=DATABASE_CONFIG['postgresql']['password'],
            database=db_name
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 启用pgvector扩展
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
        print("pgvector扩展启用成功")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print("PostgreSQL数据库初始化完成")
        
    except Exception as e:
        print(f"PostgreSQL初始化失败: {e}")

if __name__ == "__main__":
    init_postgresql()
