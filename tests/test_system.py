import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.mysql_connection import MySQLConnection
from app.database.mongodb_connection import MongoDBConnection
from app.database.postgresql_connection import PostgreSQLConnection
from app.backend.agents.xiaozhi_agent import XiaozhiAgent
from app.rag.rag_service import RAGService

def test_database_connections():
    """测试数据库连接"""
    print("测试数据库连接...")
    
    # 测试MySQL
    try:
        with MySQLConnection() as conn:
            conn.execute("SELECT 1")
            print("✅ MySQL连接成功")
    except Exception as e:
        print(f"❌ MySQL连接失败：{e}")
    
    # 测试MongoDB
    try:
        with MongoDBConnection() as conn:
            db = conn.get_db()
            print("✅ MongoDB连接成功")
    except Exception as e:
        print(f"❌ MongoDB连接失败：{e}")
    
    # 测试PostgreSQL
    try:
        with PostgreSQLConnection() as conn:
            conn.execute("SELECT 1")
            print("✅ PostgreSQL连接成功")
    except Exception as e:
        print(f"❌ PostgreSQL连接失败：{e}")

def test_ai_agent():
    """测试AI代理"""
    print("\n测试AI代理...")
    try:
        agent = XiaozhiAgent()
        response = agent.chat("test_session", "你好，你是谁？")
        print(f"✅ AI代理测试成功：{response[:50]}...")
    except Exception as e:
        print(f"❌ AI代理测试失败：{e}")

def test_rag_service():
    """测试RAG服务"""
    print("\n测试RAG服务...")
    try:
        rag_service = RAGService()
        context = rag_service.get_context("头痛怎么办？")
        print(f"✅ RAG服务测试成功，获取到上下文：{context[:100]}...")
    except Exception as e:
        print(f"❌ RAG服务测试失败：{e}")

def test_appointment_service():
    """测试预约挂号服务"""
    print("\n测试预约挂号服务...")
    try:
        agent = XiaozhiAgent()
        # 测试查询号源
        result = agent.query_department("内科", "2026-04-10", "上午")
        print(f"✅ 查询号源测试成功：{result}")
    except Exception as e:
        print(f"❌ 预约挂号服务测试失败：{e}")

if __name__ == "__main__":
    print("开始测试整个系统...")
    
    test_database_connections()
    test_ai_agent()
    test_rag_service()
    test_appointment_service()
    
    print("\n测试完成！")
