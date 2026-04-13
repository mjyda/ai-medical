import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag.rag_service import RAGService

def test_rag_service():
    print("测试修改后的RAG服务...")
    
    try:
        # 初始化RAG服务
        print("初始化RAG服务...")
        rag_service = RAGService()
        print("RAG服务初始化成功")
        
        # 加载文档
        print("加载文档...")
        doc_count = rag_service.load_documents("app/data/docs")
        print(f"成功加载 {doc_count} 个文档到知识库")
        
        # 测试检索
        print("测试检索...")
        query = "神经内科"
        context = rag_service.get_context(query)
        print(f"\n查询: {query}")
        print(f"检索到的上下文长度: {len(context)} 字符")
        if context:
            print(f"上下文预览: {context[:500]}...")
        else:
            print("未检索到相关文档")
        
        return True
        
    except Exception as e:
        print(f"RAG服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rag_service()
