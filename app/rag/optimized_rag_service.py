import uuid

from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import PGVector
from app.config.config import API_CONFIG, SYSTEM_CONFIG, DATABASE_CONFIG, CACHE_CONFIG
from app.cache.redis_cache import redis_cache
from app.rag.document_ingest import load_documents_from_file
from app.rag.text_cleaning import clean_text
import numpy as np
import requests
import json
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class OptimizedAliyunEmbeddings:
    """优化后的阿里云向量化API嵌入类"""
    
    def __init__(self):
        self.api_key = API_CONFIG['embedding_model']['api_key']
        self.model = "text-embedding-v3"
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
        self.batch_size = 10  # 保持与原始版本一致
    
    def embed_query(self, text):
        """嵌入单个查询文本"""
        embeddings = self.embed_documents([text])
        return embeddings[0] if embeddings else None
    
    def embed_documents(self, texts):
        """嵌入多个文档文本 - 支持缓存"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        all_embeddings = []
        texts_to_embed = []
        indices_to_fill = []
        
        # 先检查缓存
        for idx, text in enumerate(texts):
            cached = redis_cache.get_embedding(text)
            if cached:
                all_embeddings.append(cached)
            else:
                all_embeddings.append(None)  # 占位
                texts_to_embed.append(text)
                indices_to_fill.append(idx)
        
        print(f"缓存命中: {len(texts) - len(texts_to_embed)} 个，需要向量化: {len(texts_to_embed)} 个")
        
        # 如果全部命中缓存，直接返回
        if not texts_to_embed:
            print("全部从缓存获取")
            return all_embeddings
        
        try:
            for i in range(0, len(texts_to_embed), self.batch_size):
                batch_texts = texts_to_embed[i:i+self.batch_size]
                batch_indices = indices_to_fill[i:i+self.batch_size]
                print(f"处理批次 {i//self.batch_size + 1}/{(len(texts_to_embed)+self.batch_size-1)//self.batch_size}，文本数: {len(batch_texts)}")
                
                data = {
                    "model": self.model,
                    "input": batch_texts
                }
                
                response = requests.post(self.url, headers=headers, json=data, timeout=30)
                print(f"API响应状态码: {response.status_code}")
                response.raise_for_status()
                result = response.json()
                
                if "data" in result:
                    for j, item in enumerate(result["data"]):
                        if "embedding" in item:
                            embedding = item["embedding"]
                            all_embeddings[batch_indices[j]] = embedding
                            # 缓存结果
                            redis_cache.set_embedding(batch_texts[j], embedding, CACHE_CONFIG['embedding_ttl'])
            
            print(f"成功获取 {len(all_embeddings)} 个嵌入向量")
            return all_embeddings
        except Exception as e:
            print(f"阿里云向量化API调用失败: {e}")
            import traceback
            traceback.print_exc()
            return [e for e in all_embeddings if e is not None]
    
    async def async_embed_documents(self, texts):
        """异步嵌入多个文档文本 - 支持缓存"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 先检查缓存
        all_embeddings = []
        texts_to_embed = []
        indices_to_fill = []
        
        for idx, text in enumerate(texts):
            cached = redis_cache.get_embedding(text)
            if cached:
                all_embeddings.append(cached)
            else:
                all_embeddings.append(None)
                texts_to_embed.append(text)
                indices_to_fill.append(idx)
        
        print(f"缓存命中: {len(texts) - len(texts_to_embed)} 个，需要向量化: {len(texts_to_embed)} 个")
        
        if not texts_to_embed:
            print("全部从缓存获取")
            return all_embeddings
        
        async def process_batch(session, batch_texts, batch_indices, batch_num):
            """处理单个批次"""
            print(f"处理批次 {batch_num}，文本数: {len(batch_texts)}")
            
            data = {
                "model": self.model,
                "input": batch_texts
            }
            
            async with session.post(self.url, headers=headers, json=data, timeout=60) as response:
                print(f"批次 {batch_num} 响应状态码: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    if "data" in result:
                        embeddings = []
                        for j, item in enumerate(result["data"]):
                            if "embedding" in item:
                                embedding = item["embedding"]
                                embeddings.append((batch_indices[j], embedding))
                                # 缓存结果
                                redis_cache.set_embedding(batch_texts[j], embedding, CACHE_CONFIG['embedding_ttl'])
                        return embeddings
            return []
        
        # 将文本分成多个批次
        batches = []
        batch_indices_list = []
        for i in range(0, len(texts_to_embed), self.batch_size):
            batches.append(texts_to_embed[i:i+self.batch_size])
            batch_indices_list.append(indices_to_fill[i:i+self.batch_size])
        
        async with aiohttp.ClientSession() as session:
            # 并发处理所有批次
            tasks = [
                process_batch(session, batches[i], batch_indices_list[i], i+1)
                for i in range(len(batches))
            ]
            
            results = await asyncio.gather(*tasks)
            
            # 填充结果到正确位置
            for batch_result in results:
                for idx, embedding in batch_result:
                    all_embeddings[idx] = embedding
            
            print(f"异步处理完成，成功获取 {len(all_embeddings)} 个嵌入向量")
            return all_embeddings
    
    def parallel_embed_documents(self, texts, max_workers=4):
        """使用多线程并行嵌入文档"""
        def chunk_list(lst, n):
            """将列表分成n个子列表"""
            return [lst[i::n] for i in range(n)]
        
        def process_chunk(chunk):
            """处理单个chunk"""
            return self.embed_documents(chunk)
        
        # 将文本分成多个chunk
        chunks = chunk_list(texts, max_workers)
        
        # 使用多线程处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(process_chunk, chunks))
        
        # 合并结果
        all_embeddings = []
        for result in results:
            all_embeddings.extend(result)
        
        print(f"并行处理完成，成功获取 {len(all_embeddings)} 个嵌入向量")
        return all_embeddings

class OptimizedRAGService:
    def __init__(self):
        try:
            self.vector_store = self._init_vector_store()
            self.embeddings = OptimizedAliyunEmbeddings()
            # 文档索引跟踪，记录已处理文档的修改时间
            self.document_index = self._load_document_index()
            # 索引文件路径
            self.index_file_path = os.path.join(os.path.dirname(__file__), 'document_index.json')
        except Exception as e:
            print(f"向量存储初始化失败: {e}")
            import traceback
            traceback.print_exc()
            print("RAG功能将被禁用，但应用仍可正常运行")
            self.vector_store = None
            self.embeddings = None
            self.document_index = {}
            self.index_file_path = None
    
    def _load_document_index(self):
        """加载已处理文档的索引"""
        index_file = os.path.join(os.path.dirname(__file__), 'document_index.json')
        if os.path.exists(index_file):
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载文档索引失败: {e}")
                return {}
        return {}
    
    def _save_document_index(self):
        """保存文档索引"""
        if self.index_file_path:
            try:
                with open(self.index_file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.document_index, f, indent=2, ensure_ascii=False)
                print("文档索引已保存")
            except Exception as e:
                print(f"保存文档索引失败: {e}")
    
    def _init_vector_store(self):
        """初始化PostgreSQL向量存储"""
        embeddings = OptimizedAliyunEmbeddings()
        
        connection_string = f"postgresql://{DATABASE_CONFIG['postgresql']['user']}:{DATABASE_CONFIG['postgresql']['password']}@{DATABASE_CONFIG['postgresql']['host']}:{DATABASE_CONFIG['postgresql']['port']}/{DATABASE_CONFIG['postgresql']['database']}"
        
        vector_store = PGVector(
            collection_name="embeddings",
            connection_string=connection_string,
            embedding_function=embeddings
        )
        return vector_store
    
    def _load_single_file(self, file_path):
        """加载单个文件，支持多种格式，自动清理水印"""
        from langchain_core.documents import Document
        
        try:
            # PDF / Word：与知识库解析共用（含 OCR 回退）
            if file_path.endswith('.pdf') or file_path.endswith('.docx'):
                stable_id = str(uuid.uuid5(uuid.NAMESPACE_URL, os.path.abspath(file_path)))
                return load_documents_from_file(file_path, stable_id)
            
            # CSV格式
            elif file_path.endswith('.csv'):
                loader = CSVLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source"] = file_path
                    doc.page_content = clean_text(doc.page_content)
                return docs
            
            # Markdown和纯文本格式
            elif file_path.endswith(('.md', '.txt')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content = clean_text(content)
                    return [Document(page_content=content, metadata={"source": file_path})]
            
            else:
                print(f"不支持的文件格式: {file_path}")
                return []
                
        except Exception as e:
            print(f"加载文件 {file_path} 失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def load_documents_parallel(self, directory, max_workers=4):
        """并行加载文档"""
        if not self.vector_store:
            return 0
        
        try:
            print(f"文档目录: {directory}")
            
            # 获取所有文件路径
            all_files = []
            for file in os.listdir(directory):
                if file.endswith(('.md', '.txt', '.pdf', '.docx', '.csv')):
                    all_files.append(os.path.join(directory, file))
            
            print(f"待处理文件数: {len(all_files)}")
            
            # 使用多线程并行加载文件
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(self._load_single_file, all_files))
            
            # 合并结果
            documents = []
            for result in results:
                documents.extend(result)
            
            print(f"总文档数: {len(documents)}")
            
            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            split_docs = text_splitter.split_documents(documents)
            print(f"分割后文档数: {len(split_docs)}")
            
            # 批量存储到向量库
            self._batch_add_documents(split_docs, batch_size=50)
            
            return len(split_docs)
        except Exception as e:
            print(f"加载文档失败: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def _batch_add_documents(self, docs, batch_size=50):
        """批量添加文档到向量库"""
        if not docs:
            print("没有文档需要存储")
            return
        
        print(f"开始批量存储文档，共 {len(docs)} 个文档，批次大小: {batch_size}")
        
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i+batch_size]
            print(f"存储批次 {i//batch_size + 1}/{(len(docs)+batch_size-1)//batch_size}，文档数: {len(batch_docs)}")
            
            try:
                self.vector_store.add_documents(batch_docs)
                print(f"批次 {i//batch_size + 1} 存储成功")
            except Exception as e:
                print(f"批次 {i//batch_size + 1} 存储失败: {e}")
        
        print(f"成功存储 {len(docs)} 个文档到向量库")
    
    def ingest_file_for_doc(self, doc_id: str, file_path: str) -> int:
        """将单个已上传文件切分并写入向量库，chunk metadata 含 doc_id。"""
        if not self.vector_store:
            raise RuntimeError("向量存储未初始化")
        documents = load_documents_from_file(file_path, doc_id)
        if not documents:
            return 0
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        split_docs = text_splitter.split_documents(documents)
        self._batch_add_documents(split_docs, batch_size=50)
        return len(split_docs)
    
    async def load_documents_async(self, directory):
        """异步加载文档"""
        if not self.vector_store:
            return 0
        
        try:
            print(f"文档目录: {directory}")
            
            # 获取所有文件路径
            all_files = []
            for file in os.listdir(directory):
                if file.endswith(('.md', '.txt')):
                    all_files.append(os.path.join(directory, file))
            
            # 异步读取文本文件
            async def read_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        from langchain_core.documents import Document
                        return Document(page_content=content, metadata={"source": file_path})
                except Exception as e:
                    print(f"读取文件 {file_path} 失败: {e}")
                    return None
            
            tasks = [read_file(file) for file in all_files]
            documents = await asyncio.gather(*tasks)
            documents = [doc for doc in documents if doc]
            
            print(f"总文档数: {len(documents)}")
            
            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            split_docs = text_splitter.split_documents(documents)
            print(f"分割后文档数: {len(split_docs)}")
            
            # 提取文本内容进行向量化
            texts = [doc.page_content for doc in split_docs]
            
            # 使用异步向量化
            embeddings = await self.embeddings.async_embed_documents(texts)
            
            if embeddings:
                # 将嵌入向量添加到向量库
                print("开始存储文档到向量库...")
                self.vector_store.add_documents(split_docs)
                print(f"成功存储 {len(split_docs)} 个文档到向量库")
            
            return len(split_docs)
        except Exception as e:
            print(f"异步加载文档失败: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def _get_file_modification_time(self, file_path):
        """获取文件的修改时间"""
        try:
            return os.path.getmtime(file_path)
        except Exception as e:
            print(f"获取文件修改时间失败: {e}")
            return 0
    
    def update_documents_incrementally(self, directory):
        """增量更新文档：只处理新增或修改的文档"""
        if not self.vector_store:
            return 0
        
        try:
            print(f"开始增量更新，文档目录: {directory}")
            
            # 获取所有文件路径
            all_files = []
            for file in os.listdir(directory):
                if file.endswith(('.md', '.txt', '.pdf', '.docx', '.csv')):
                    all_files.append(os.path.join(directory, file))
            
            print(f"目录中文件总数: {len(all_files)}")
            
            # 找出新增或修改的文件
            changed_files = []
            deleted_files = []
            
            # 检查新增或修改的文件
            for file_path in all_files:
                file_key = file_path.replace('\\', '/')
                current_mtime = self._get_file_modification_time(file_path)
                stored_mtime = self.document_index.get(file_key, 0)
                
                if current_mtime > stored_mtime:
                    changed_files.append(file_path)
                    print(f"检测到新增或修改的文件: {file_path}")
            
            # 检查已删除的文件
            for file_key in list(self.document_index.keys()):
                local_path = file_key.replace('/', '\\')
                if not os.path.exists(local_path):
                    deleted_files.append(file_key)
                    print(f"检测到已删除的文件: {file_key}")
            
            print(f"需要新增/更新的文件数: {len(changed_files)}")
            print(f"需要删除的文件数: {len(deleted_files)}")
            
            # 处理新增或修改的文件
            if changed_files:
                # 使用多线程并行加载文件
                with ThreadPoolExecutor(max_workers=4) as executor:
                    results = list(executor.map(self._load_single_file, changed_files))
                
                # 合并结果
                documents = []
                for result in results:
                    documents.extend(result)
                
                print(f"待处理文档数: {len(documents)}")
                
                # 分割文档
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                split_docs = text_splitter.split_documents(documents)
                print(f"分割后文档数: {len(split_docs)}")
                
                # 批量存储到向量库
                self._batch_add_documents(split_docs, batch_size=50)
                
                # 更新文档索引
                for file_path in changed_files:
                    file_key = file_path.replace('\\', '/')
                    self.document_index[file_key] = self._get_file_modification_time(file_path)
            
            # 处理已删除的文件（从索引中移除）
            if deleted_files:
                for file_key in deleted_files:
                    del self.document_index[file_key]
                    # 注意：从向量库中删除文档需要根据metadata查询删除
                    # 这里简化处理，只更新索引
                    print(f"已从索引中移除: {file_key}")
            
            # 保存更新后的索引
            self._save_document_index()
            
            return len(changed_files)
        except Exception as e:
            print(f"增量更新失败: {e}")
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
    
    def retrieve_with_source(self, query, k=5, score_threshold=0.5):
        """检索相关文档并返回来源信息（答案溯源）"""
        if not self.vector_store:
            return []
        
        try:
            print(f"检索查询: {query}")
            documents = self.vector_store.similarity_search_with_relevance_scores(
                query,
                k=k
            )
            
            # 过滤低相似度的文档并提取来源信息
            results_with_source = []
            for doc, score in documents:
                if score >= score_threshold:
                    source_info = {
                        'content': doc.page_content,
                        'source': doc.metadata.get('source', '未知来源'),
                        'score': score,
                        'page': doc.metadata.get('page', 0)
                    }
                    results_with_source.append(source_info)
            
            print(f"溯源结果数: {len(results_with_source)}")
            return results_with_source
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
    
    def get_context_with_sources(self, query):
        """获取查询的上下文信息及来源（用于答案溯源）"""
        results = self.retrieve_with_source(query)
        
        if not results:
            return {"context": "", "sources": []}
        
        # 构建上下文
        context = "\n".join([result['content'] for result in results])
        
        # 提取来源信息
        sources = []
        for result in results:
            source_info = {
                'file': os.path.basename(result['source']),
                'full_path': result['source'],
                'relevance_score': round(result['score'], 4),
                'page': result['page']
            }
            sources.append(source_info)
        
        return {
            "context": context,
            "sources": sources
        }
