"""
彻底修复RAG检索问题 - 清空数据库和缓存
"""

import os
import sys
import importlib
import psycopg2
from app.config.config import DATABASE_CONFIG

# 清理Python模块缓存
def clear_module_cache():
    """清理Python模块缓存"""
    print("\n清理Python模块缓存...")
    
    # 移除可能的.pyc文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"  删除: {pyc_path}")
                except Exception as e:
                    pass
    
    # 重新加载相关模块
    modules_to_reload = [
        'app.rag.rag_service',
        'app.config.config'
    ]
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            print(f"  重新加载模块: {module_name}")
            importlib.reload(sys.modules[module_name])

# 清空数据库
def clear_database():
    """清空向量数据库"""
    print("\n清空向量数据库...")
    
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
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        
        # 清空所有表
        for table in tables:
            table_name = table[0]
            if 'langchain' in table_name.lower():
                try:
                    cursor.execute(f"DELETE FROM {table_name}")
                    print(f"  清空表: {table_name}")
                except Exception as e:
                    print(f"  清空表 {table_name} 失败: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("  数据库清空完成")
        return True
    except Exception as e:
        print(f"  清空数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 验证文件内容
def verify_file_content():
    """验证文件内容"""
    print("\n验证文档文件内容...")
    
    file_path = "app/data/docs/公司简介.md"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  文件: {file_path}")
            print(f"  内容包含 'wootion': {'wootion' in content}")
            print(f"  内容包含 'info@example.com': {'info@example.com' in content}")
            print(f"  内容包含 'wootion@example.com': {'wootion@example.com' in content}")
            
            # 显示联系方式部分
            lines = content.split('\n')
            in_contact = False
            for line in lines:
                if '联系方式' in line:
                    in_contact = True
                if in_contact:
                    print(f"    {line}")
                    if line.strip() == '' and in_contact:
                        break
    else:
        print(f"  文件不存在: {file_path}")

# 重新加载文档
def reload_documents():
    """重新加载文档"""
    print("\n重新加载文档...")
    
    # 延迟导入，确保模块已重新加载
    from app.rag.rag_service import RAGService
    
    rag_service = RAGService()
    if rag_service.vector_store is None:
        print("  RAG服务初始化失败")
        return 0
    
    count = rag_service.load_documents("app/data/docs")
    print(f"  成功加载 {count} 个文档")
    return count

# 测试检索
def test_retrieval():
    """测试检索"""
    print("\n测试检索功能...")
    
    from app.rag.rag_service import RAGService
    
    rag_service = RAGService()
    
    test_queries = ["公司联系方式", "公司邮箱", "官方网站"]
    
    for query in test_queries:
        print(f"\n  查询: {query}")
        context = rag_service.get_context(query)
        
        if context:
            print(f"  检索结果包含 'wootion': {'wootion' in context}")
            print(f"  检索结果包含 'info@example.com': {'info@example.com' in context}")
            print(f"  检索结果包含 'wootion@example.com': {'wootion@example.com' in context}")
        else:
            print("  未检索到内容")

# 主函数
def main():
    """主函数"""
    print("=" * 60)
    print("彻底修复RAG检索问题")
    print("=" * 60)
    
    # 1. 验证文件内容
    verify_file_content()
    
    # 2. 清理模块缓存
    clear_module_cache()
    
    # 3. 清空数据库
    clear_database()
    
    # 4. 重新加载文档
    reload_documents()
    
    # 5. 测试检索
    test_retrieval()
    
    print("\n" + "=" * 60)
    print("修复完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
