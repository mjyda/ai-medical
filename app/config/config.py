import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置（本地对话模型：网线/无线网段不同，见 docker-compose 或 .env 中 LOCAL_LLM_*）
API_CONFIG = {
    "local_model": {
        "base_url": os.getenv(
            "LOCAL_LLM_BASE_URL",
            "http://10.204.220.21:8000/v1",
        ),
        "api_key": os.getenv(
            "LOCAL_LLM_API_KEY",
            "sk-95ec443dc9594cab9fc7e96fff5f201f",
        ),
        "model_name": os.getenv("LOCAL_LLM_MODEL_NAME", "qwen3-coder-30b"),
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
        # 与 docker-compose 宿主机映射 5434:5432 对齐；直连容器内 postgres 用 5432
        "port": int(os.getenv("POSTGRESQL_PORT", "5434")),
        "database": os.getenv("POSTGRESQL_DATABASE", "vector_db"),
        "user": os.getenv("POSTGRESQL_USER", "postgres"),
        "password": os.getenv("POSTGRESQL_PASSWORD", "password")
    }
}

# Celery（文档解析/向量化异步任务）
CELERY_CONFIG = {
    "broker_url": os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    "result_backend": os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
}

# 文档知识库（上传、OCR、API）
KNOWLEDGE_BASE_CONFIG = {
    "upload_dir": os.getenv("KB_UPLOAD_DIR", "app/data/uploads"),
    "max_upload_bytes": int(os.getenv("KB_MAX_UPLOAD_BYTES", str(100 * 1024 * 1024))),
    # 无 Celery worker 时可在开发环境走同步路径（pytest 可开启）
    "doc_sync_ingest": os.getenv("KB_DOC_SYNC_INGEST", "false").lower() == "true",
    "ocr_enabled": os.getenv("KB_OCR_ENABLED", "true").lower() == "true",
    "ocr_min_chars_per_page": int(os.getenv("KB_OCR_MIN_CHARS_PER_PAGE", "50")),
    # 后续可接 minio://bucket/...
    "storage_backend": os.getenv("KB_STORAGE_BACKEND", "local"),
    "api_base_url": os.getenv("DOC_API_BASE_URL", "http://127.0.0.1:8001"),
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

# 视频配置
VIDEO_CONFIG = {
    "upload_dir": os.getenv("VIDEO_UPLOAD_DIR", "app/data/uploads/videos"),
    "max_upload_bytes": int(os.getenv("VIDEO_MAX_UPLOAD_BYTES", str(500 * 1024 * 1024))),
    "allowed_extensions": os.getenv("VIDEO_ALLOWED_EXTENSIONS", ".mp4,.avi,.mov,.mkv,.webm").split(","),
    # 在线下载配置
    "download_max_height": int(os.getenv("VIDEO_DOWNLOAD_MAX_HEIGHT", "1080")),
    "download_timeout": int(os.getenv("VIDEO_DOWNLOAD_TIMEOUT", "600")),
    "download_cookies_file": os.getenv("VIDEO_DOWNLOAD_COOKIES_FILE", ""),
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
    },
    "knowledge_base": {
        "upload_dir": KNOWLEDGE_BASE_CONFIG["upload_dir"],
        "max_upload_bytes": KNOWLEDGE_BASE_CONFIG["max_upload_bytes"],
    }
}