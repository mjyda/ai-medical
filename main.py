import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.backend.agents.xiaozhi_agent import XiaozhiAgent
from app.rag.rag_service import RAGService


def initialize_app():
    """初始化应用"""
    print("正在初始化硅谷小智医疗智能助手...")
    
    # 初始化RAG服务并加载文档
    rag_service = RAGService()
    try:
        # 加载知识库文档
        doc_count = rag_service.load_documents("app/data/docs")
        print(f"成功加载 {doc_count} 个文档到知识库")
    except Exception as e:
        print(f"加载文档时出错: {e}")
    
    # 初始化AI代理
    agent = XiaozhiAgent()
    print("AI代理初始化完成")
    
    return agent


def start_streamlit():
    """启动Streamlit应用"""
    print("启动Streamlit前端...")
    os.system("streamlit run app/frontend/app.py")


if __name__ == "__main__":
    # 初始化应用
    agent = initialize_app()
    
    # 启动Streamlit
    start_streamlit()
