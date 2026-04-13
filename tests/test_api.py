import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.config import API_CONFIG
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

def test_local_model():
    """测试本地大模型连接"""
    print("测试本地大模型连接...")
    try:
        llm = ChatOpenAI(
            api_key=API_CONFIG['local_model']['api_key'],
            model=API_CONFIG['local_model']['model_name'],
            base_url=API_CONFIG['local_model']['base_url'],
            temperature=0.7
        )
        
        response = llm.invoke("你好，你是谁？")
        print(f"本地模型测试成功：{response.content}")
        return True
    except Exception as e:
        print(f"本地模型测试失败：{e}")
        return False

def test_embedding_model():
    """测试向量模型连接"""
    print("测试向量模型连接...")
    try:
        embeddings = OpenAIEmbeddings(
            api_key=API_CONFIG['embedding_model']['api_key'],
            model=API_CONFIG['embedding_model']['model_name'],
            base_url=API_CONFIG['embedding_model']['base_url']
        )
        
        # 测试生成嵌入向量
        vectors = embeddings.embed_query("测试向量生成")
        print(f"向量模型测试成功，向量维度：{len(vectors)}")
        return True
    except Exception as e:
        print(f"向量模型测试失败：{e}")
        return False

if __name__ == "__main__":
    print("开始测试API连接...")
    
    local_model_ok = test_local_model()
    embedding_model_ok = test_embedding_model()
    
    if local_model_ok and embedding_model_ok:
        print("\n✅ 所有API测试通过！")
    else:
        print("\n❌ 部分API测试失败，请检查配置！")
