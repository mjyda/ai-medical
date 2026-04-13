import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.mysql_connection import MySQLConnection

def check_tables():
    print("检查MySQL表结构...")
    
    try:
        with MySQLConnection() as conn:
            # 检查appointment表结构
            conn.execute("DESCRIBE appointment")
            columns = conn.fetch_all()
            print("\nappointment表结构:")
            for col in columns:
                print(f"  {col['Field']}: {col['Type']}")
            
            # 检查department表结构
            conn.execute("DESCRIBE department")
            columns = conn.fetch_all()
            print("\ndepartment表结构:")
            for col in columns:
                print(f"  {col['Field']}: {col['Type']}")
            
            # 检查doctor表结构
            conn.execute("DESCRIBE doctor")
            columns = conn.fetch_all()
            print("\ndoctor表结构:")
            for col in columns:
                print(f"  {col['Field']}: {col['Type']}")
            
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    check_tables()
