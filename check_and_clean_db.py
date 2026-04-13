"""
检查并清理PostgreSQL向量数据库
"""

import psycopg2
from app.config.config import DATABASE_CONFIG

def check_and_clean_db():
    """检查并清理数据库"""
    print("=" * 50)
    print("检查PostgreSQL向量数据库")
    print("=" * 50)
    
    try:
        # 连接PostgreSQL
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['postgresql']['host'],
            port=DATABASE_CONFIG['postgresql']['port'],
            database=DATABASE_CONFIG['postgresql']['database'],
            user=DATABASE_CONFIG['postgresql']['user'],
            password=DATABASE_CONFIG['postgresql']['password']
        )
        
        cursor = conn.cursor()
        
        # 查看所有表
        print("\n数据库中的表:")
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        
        # 查看langchain_pg_collection表
        print("\n集合信息:")
        try:
            cursor.execute("SELECT * FROM langchain_pg_collection")
            collections = cursor.fetchall()
            for col in collections:
                print(f"  {col}")
        except:
            print("  表不存在或为空")
        
        # 查看langchain_pg_embedding表中的数据量
        print("\n向量数据数量:")
        try:
            cursor.execute("SELECT COUNT(*) FROM langchain_pg_embedding")
            count = cursor.fetchone()[0]
            print(f"  共有 {count} 条向量数据")
            
            # 查看部分数据内容
            if count > 0:
                print("\n部分向量数据内容:")
                cursor.execute("SELECT document, cmetadata FROM langchain_pg_embedding LIMIT 3")
                rows = cursor.fetchall()
                for i, row in enumerate(rows):
                    print(f"\n  文档 {i+1}:")
                    print(f"    内容: {row[0][:100]}...")
                    print(f"    元数据: {row[1]}")
        except:
            print("  表不存在或为空")
        
        # 清理所有数据
        print("\n" + "=" * 50)
        print("清理所有向量数据...")
        print("=" * 50)
        
        for table in tables:
            table_name = table[0]
            if 'langchain' in table_name.lower():
                try:
                    cursor.execute(f"DELETE FROM {table_name}")
                    print(f"[OK] 清理表 {table_name}")
                except Exception as e:
                    print(f"[ERROR] 清理表 {table_name} 失败: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n[OK] 数据库清理完成")
        
    except Exception as e:
        print(f"[ERROR] 操作失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_and_clean_db()
