import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API配置
API_CONFIG = {
    "local_model": {
        "base_url": "http://10.204.220.21:8000/v1",
        "api_key": "sk-95ec443dc9594cab9fc7e96fff5f201f",
        "model_name": "qwen3-coder-30b"
    },
    "embedding_model": {
        "api_key": "sk-95ec443dc9594cab9fc7e96fff5f201f",
        "model_name": "text-embedding-v3",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
    }
}

# 数据库配置（优先从环境变量读取，支持Docker容器环境）
DATABASE_CONFIG = {
    "mysql": {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "database": os.getenv("MYSQL_DATABASE", "guiguxiaozhi"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "123456")
    },
    "mongodb": {
        "host": os.getenv("MONGODB_HOST", "localhost"),
        "port": int(os.getenv("MONGODB_PORT", "27017")),
        "database": os.getenv("MONGODB_DATABASE", "chat_memory_db")
    },
    "postgresql": {
        "host": os.getenv("POSTGRESQL_HOST", "localhost"),
        "port": int(os.getenv("POSTGRESQL_PORT", "5433")),
        "database": os.getenv("POSTGRESQL_DATABASE", "vector_db"),
        "user": os.getenv("POSTGRESQL_USER", "postgres"),
        "password": os.getenv("POSTGRESQL_PASSWORD", "password")
    }
}

# 缓存配置（优先从环境变量读取，支持Docker容器环境）
CACHE_CONFIG = {
    "redis": {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_DB", "0"))
    },
    "embedding_ttl": 3600 * 24 * 7,  # 嵌入向量缓存7天
    "query_ttl": 3600  # 查询结果缓存1小时
}

# 系统配置
SYSTEM_CONFIG = {
    "rag": {
        "document_dir": "app/data/docs",
        "max_results": 3,
        "similarity_threshold": 0.8
    },
    "chat": {
        "max_history": 20,
        "temperature": 0.7
    },
    "concurrency": {
        "max_workers": 10,
        "batch_size": 50,
        "async_timeout": 60
    }
}