import redis
import json
import hashlib
from app.config.config import CACHE_CONFIG

class RedisCache:
    """Redis缓存服务 - 支持高并发场景"""
    
    def __init__(self):
        try:
            self.client = redis.Redis(
                host=CACHE_CONFIG['redis']['host'],
                port=CACHE_CONFIG['redis']['port'],
                db=CACHE_CONFIG['redis']['db'],
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                max_connections=100  # 连接池大小
            )
            # 测试连接
            self.client.ping()
            print("Redis缓存服务初始化成功")
        except Exception as e:
            print(f"Redis缓存服务初始化失败: {e}")
            self.client = None
    
    def _get_key(self, prefix, text):
        """生成缓存键"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{prefix}:{text_hash}"
    
    def get_embedding(self, text):
        """获取文本的嵌入向量缓存"""
        if not self.client:
            return None
        
        key = self._get_key("embedding", text)
        try:
            cached = self.client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"获取嵌入向量缓存失败: {e}")
            return None
    
    def set_embedding(self, text, embedding, ttl=3600*24*7):
        """设置文本的嵌入向量缓存"""
        if not self.client:
            return False
        
        key = self._get_key("embedding", text)
        try:
            self.client.set(key, json.dumps(embedding), ex=ttl)
            return True
        except Exception as e:
            print(f"设置嵌入向量缓存失败: {e}")
            return False
    
    def get_query_result(self, query):
        """获取查询结果缓存"""
        if not self.client:
            return None
        
        key = self._get_key("query", query)
        try:
            cached = self.client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"获取查询结果缓存失败: {e}")
            return None
    
    def set_query_result(self, query, result, ttl=3600):
        """设置查询结果缓存"""
        if not self.client:
            return False
        
        key = self._get_key("query", query)
        try:
            self.client.set(key, json.dumps(result), ex=ttl)
            return True
        except Exception as e:
            print(f"设置查询结果缓存失败: {e}")
            return False
    
    def invalidate_doc_cache(self, doc_path):
        """使指定文档相关的缓存失效"""
        if not self.client:
            return False
        
        try:
            # 删除与该文档相关的查询缓存
            pattern = f"query:*"
            keys = self.client.keys(pattern)
            for key in keys:
                self.client.delete(key)
            print(f"已清除 {len(keys)} 个查询缓存")
            return True
        except Exception as e:
            print(f"清除缓存失败: {e}")
            return False
    
    def flush_all(self):
        """清空所有缓存"""
        if not self.client:
            return False
        
        try:
            self.client.flushall()
            print("所有缓存已清空")
            return True
        except Exception as e:
            print(f"清空缓存失败: {e}")
            return False

# 全局缓存实例
redis_cache = RedisCache()