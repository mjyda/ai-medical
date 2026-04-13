"""
测试RAG检索功能
"""

from app.rag.rag_service import RAGService

def test_rag_retrieval():
    """测试RAG检索"""
    print("=" * 50)
    print("测试RAG检索功能")
    print("=" * 50)
    
    # 初始化RAG服务
    print("\n1. 初始化RAG服务...")
    rag_service = RAGService()
    
    if rag_service.vector_store is None:
        print("[ERROR] RAG服务初始化失败")
        return
    
    print("[OK] RAG服务初始化成功")
    
    # 测试检索
    test_queries = [
        "公司的联系方式是什么？",
        "公司邮箱",
        "公司地址",
        "联系电话"
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 50}")
        print(f"测试查询: {query}")
        print(f"{'=' * 50}")
        
        context = rag_service.get_context(query)
        
        if context:
            print(f"\n检索到的上下文:\n{context}")
        else:
            print("\n[WARNING] 未检索到任何上下文")
    
    print(f"\n{'=' * 50}")
    print("测试完成")
    print(f"{'=' * 50}")

if __name__ == "__main__":
    test_rag_retrieval()
