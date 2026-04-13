import mysql.connector.pooling
from pymongo import MongoClient
import psycopg2.pool
from app.config.config import DATABASE_CONFIG

class MySQLConnectionPool:
    """MySQL连接池"""
    def __init__(self):
        try:
            config = DATABASE_CONFIG['mysql']
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mysql_pool",
                pool_size=5,
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
        except Exception as e:
            print(f"MySQL连接池初始化失败: {e}")
            self.pool = None
    
    def get_connection(self):
        if self.pool:
            return self.pool.get_connection()
        return None

class PostgreSQLConnectionPool:
    """PostgreSQL连接池"""
    def __init__(self):
        try:
            config = DATABASE_CONFIG['postgresql']
            self.pool = psycopg2.pool.SimpleConnectionPool(
                1,
                5,
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
        except Exception as e:
            print(f"PostgreSQL连接池初始化失败: {e}")
            self.pool = None
    
    def get_connection(self):
        if self.pool:
            return self.pool.getconn()
        return None
    
    def put_connection(self, conn):
        if self.pool and conn:
            self.pool.putconn(conn)

# 全局连接池实例
mysql_pool = MySQLConnectionPool()
postgres_pool = PostgreSQLConnectionPool()

try:
    mongodb_client = MongoClient(
        host=DATABASE_CONFIG['mongodb']['host'],
        port=DATABASE_CONFIG['mongodb']['port']
    )
    mongodb_db = mongodb_client[DATABASE_CONFIG['mongodb']['database']]
except Exception as e:
    print(f"MongoDB连接初始化失败: {e}")
    mongodb_client = None
    mongodb_db = None
