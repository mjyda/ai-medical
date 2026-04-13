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

# 数据库配置
DATABASE_CONFIG = {
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "database": "guiguxiaozhi",
        "user": "root",
        "password": "123456"
    },
    "mongodb": {
        "host": "localhost",
        "port": 27017,
        "database": "chat_memory_db"
    },
    "postgresql": {
        "host": "localhost",
        "port": 5433,
        "database": "vector_db",
        "user": "postgres",
        "password": "password"
    }
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
    }
}