"""从项目根目录运行: python scripts/init_knowledge_base.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.rag.optimized_rag_service import OptimizedRAGService
from app.config.config import SYSTEM_CONFIG


def init_knowledge_base():
    """初始化知识库"""
    print("开始初始化知识库...")

    try:
        print("1. 初始化RAG服务...")
        rag_service = OptimizedRAGService()
        print("RAG服务初始化成功")

        print("2. 加载文档...")
        document_dir = SYSTEM_CONFIG['rag']['document_dir']
        doc_count = rag_service.load_documents_parallel(document_dir, max_workers=4)
        print(f"成功加载 {doc_count} 个文档到知识库")

        print("\n知识库初始化完成！")
        return True

    except Exception as e:
        print(f"知识库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    init_knowledge_base()
