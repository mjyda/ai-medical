"""从项目根目录运行: python scripts/reset_knowledge_base.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import psycopg2
from app.config.config import DATABASE_CONFIG
from app.rag.rag_service import RAGService


def reset_vector_store():
    """清空向量数据库"""
    print("正在连接PostgreSQL数据库...")
    try:
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['postgresql']['host'],
            port=DATABASE_CONFIG['postgresql']['port'],
            database=DATABASE_CONFIG['postgresql']['database'],
            user=DATABASE_CONFIG['postgresql']['user'],
            password=DATABASE_CONFIG['postgresql']['password']
        )

        cursor = conn.cursor()

        cursor.execute("DELETE FROM langchain_pg_embedding")
        cursor.execute("DELETE FROM langchain_pg_collection")

        conn.commit()
        cursor.close()
        conn.close()

        print("[OK] 向量数据库已清空")
        return True
    except Exception as e:
        print(f"[ERROR] 清空向量数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def reinit_knowledge_base():
    """重新初始化知识库"""
    print("=" * 50)
    print("开始重置知识库...")
    print("=" * 50)

    print("\n步骤1: 清空向量数据库...")
    if not reset_vector_store():
        print("清空失败，继续执行...")

    print("\n步骤2: 初始化RAG服务...")
    rag_service = RAGService()

    if rag_service.vector_store is None:
        print("[ERROR] RAG服务初始化失败")
        return

    print("[OK] RAG服务初始化成功")

    print("\n步骤3: 加载文档...")
    document_dir = "app/data/docs"
    count = rag_service.load_documents(document_dir)

    print(f"\n{'=' * 50}")
    print(f"[OK] 知识库重置完成！成功加载 {count} 个文档")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    reinit_knowledge_base()
