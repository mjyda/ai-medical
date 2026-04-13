from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from app.config.config import API_CONFIG, SYSTEM_CONFIG, DATABASE_CONFIG
import numpy as np
import requests
import json
import os

class AliyunEmbeddings:
    """阿里云向量化API的嵌入类"""
    
    def __init__(self):
        self.api_key = API_CONFIG['embedding_model']['api_key']
        self.model = "text-embedding-v3"
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
    
    def embed_query(self, text):
        """嵌入单个查询文本"""
        embeddings = self.embed_documents([text])
        return embeddings[0] if embeddings else None
    
    def embed_documents(self, texts):
        """嵌入多个文档文本"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 批量处理，每次最多10个文本
        batch_size = 10
        all_embeddings = []
        
        try:
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                print(f"处理批次 {i//batch_size + 1}/{(len(texts)+batch_size-1)//batch_size}，文本数: {len(batch_texts)}")
                
                # 构建请求体
                data = {
                    "model": self.model,
                    "input": batch_texts
                }
                
                response = requests.post(self.url, headers=headers, json=data, timeout=30)
                print(f"API响应状态码: {response.status_code}")
                response.raise_for_status()
                result = response.json()
                
                # 提取嵌入向量
                if "data" in result:
                    for item in result["data"]:
                        if "embedding" in item:
                            all_embeddings.append(item["embedding"])
            
            print(f"成功获取 {len(all_embeddings)} 个嵌入向量")
            return all_embeddings
        except Exception as e:
            print(f"阿里云向量化API调用失败: {e}")
            import traceback
            traceback.print_exc()
            return []

class RAGService:
    def __init__(self):
        # 初始化向量存储
        try:
            self.vector_store = self._init_vector_store()
        except Exception as e:
            print(f"向量存储初始化失败: {e}")
            import traceback
            traceback.print_exc()
            print("RAG功能将被禁用，但应用仍可正常运行")
            self.vector_store = None
    
    def _init_vector_store(self):
        """初始化PostgreSQL向量存储"""
        # 使用阿里云向量化API
        embeddings = AliyunEmbeddings()
        
        connection_string = f"postgresql://{DATABASE_CONFIG['postgresql']['user']}:{DATABASE_CONFIG['postgresql']['password']}@{DATABASE_CONFIG['postgresql']['host']}:{DATABASE_CONFIG['postgresql']['port']}/{DATABASE_CONFIG['postgresql']['database']}"
        
        vector_store = PGVector(
            collection_name="embeddings",
            connection_string=connection_string,
            embedding_function=embeddings
        )
        return vector_store
    
    def load_documents(self, directory):
        """加载文档"""
        if not self.vector_store:
            return 0
        
        try:
            print(f"文档目录: {directory}")
            print(f"目录是否存在: {os.path.exists(directory)}")
            
            # 列出目录中的文件
            if os.path.exists(directory):
                files = os.listdir(directory)
                print(f"目录中的文件: {files}")
            
            # 手动加载文档
            documents = []
            
            # 加载md和txt文件
            for file in os.listdir(directory):
                if file.endswith('.md') or file.endswith('.txt'):
                    file_path = os.path.join(directory, file)
                    print(f"加载文件: {file_path}")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            from langchain_core.documents import Document
                            doc = Document(page_content=content, metadata={"source": file_path})
                            documents.append(doc)
                    except Exception as e:
                        print(f"加载文件 {file} 失败: {e}")
            
            # 加载pdf文件
            for file in os.listdir(directory):
                if file.endswith('.pdf'):
                    file_path = os.path.join(directory, file)
                    print(f"加载PDF文件: {file_path}")
                    try:
                        loader = PyPDFLoader(file_path)
                        pdf_docs = loader.load()
                        documents.extend(pdf_docs)
                    except Exception as e:
                        print(f"加载PDF文件 {file} 失败: {e}")
            
            print(f"总文档数: {len(documents)}")
            
            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            split_docs = text_splitter.split_documents(documents)
            print(f"分割后文档数: {len(split_docs)}")
            
            # 存储到向量库
            if split_docs:
                print("开始存储文档到向量库...")
                self.vector_store.add_documents(split_docs)
                print(f"成功存储 {len(split_docs)} 个文档到向量库")
            else:
                print("没有文档需要存储")
            
            return len(split_docs)
        except Exception as e:
            print(f"加载文档失败: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def retrieve_relevant_documents(self, query, k=5, score_threshold=0.5):
        """检索相关文档"""
        if not self.vector_store:
            return []
        
        try:
            print(f"检索查询: {query}")
            documents = self.vector_store.similarity_search_with_relevance_scores(
                query,
                k=k
            )
            
            print(f"原始检索结果: {[(doc.page_content[:50] + '...', score) for doc, score in documents]}")
            
            # 过滤低相似度的文档
            relevant_docs = [doc for doc, score in documents if score >= score_threshold]
            print(f"过滤后文档数: {len(relevant_docs)}")
            
            return relevant_docs
        except Exception as e:
            print(f"检索文档失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_context(self, query):
        """获取查询的上下文信息"""
        docs = self.retrieve_relevant_documents(query)
        context = "\n".join([doc.page_content for doc in docs])
        print(f"获取到的上下文长度: {len(context)}")
        if context:
            print(f"上下文内容: {context[:200]}...")
        return context