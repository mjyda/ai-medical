import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.mysql_connection import MySQLConnection
from app.database.mongodb_connection import MongoDBConnection
from app.database.postgresql_connection import PostgreSQLConnection

def test_mysql_connection():
    print("测试MySQL连接...")
    try:
        with MySQLConnection() as conn:
            conn.execute("SELECT 1")
            result = conn.fetch_one()
            print(f"MySQL连接成功: {result}")
        return True
    except Exception as e:
        print(f"MySQL连接失败: {e}")
        return False

def test_mongodb_connection():
    print("测试MongoDB连接...")
    try:
        conn = MongoDBConnection()
        db = conn.get_db()
        collections = db.list_collection_names()
        print(f"MongoDB连接成功，集合数量: {len(collections)}")
        return True
    except Exception as e:
        print(f"MongoDB连接失败: {e}")
        return False

def test_postgresql_connection():
    print("测试PostgreSQL连接...")
    try:
        with PostgreSQLConnection() as conn:
            conn.execute("SELECT 1")
            result = conn.fetch_one()
            print(f"PostgreSQL连接成功: {result}")
        return True
    except Exception as e:
        print(f"PostgreSQL连接失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试数据库连接...")
    
    mysql_ok = test_mysql_connection()
    mongodb_ok = test_mongodb_connection()
    postgresql_ok = test_postgresql_connection()
    
    print("\n测试结果:")
    print(f"MySQL: {'成功' if mysql_ok else '失败'}")
    print(f"MongoDB: {'成功' if mongodb_ok else '失败'}")
    print(f"PostgreSQL: {'成功' if postgresql_ok else '失败'}")
