# 硅谷小智 - 医疗智能助手（Python版）

## 项目简介

这是一个基于Python和Streamlit开发的医疗智能助手系统，集成了大模型AI能力，提供医疗咨询和挂号服务。

## 技术栈

- **前端**：Streamlit 1.36.0（内部演示）；产品 UI 见 `web/`（React + Vite + Tailwind + shadcn 风格组件，见 `Spec-coding/jishuzhan/tech_stack_spec.md`）
- **后端**：Python 3.8+
- **AI框架**：LangChain 0.2.15
- **大模型**：本地部署的 qwen3-coder-30b
- **向量模型**：阿里云 text-embedding-v3
- **数据库**：
  - MySQL（预约挂号数据）
  - MongoDB（对话历史）
  - PostgreSQL（向量存储）

## 功能特性

1. **医疗咨询**：基于大模型提供医疗建议
2. **AI分导诊**：智能推荐合适的科室
3. **预约挂号**：在线预约、取消预约、查询号源
4. **知识库检索**：基于RAG技术的医疗知识检索
5. **对话记忆**：支持多轮对话，保持上下文

## 项目结构

```
python-ai-medical/
├── app/
│   ├── backend/
│   │   ├── agents/              # AI 代理（如 medical_chat_agent.py）
│   │   └── services/            # 业务服务
│   ├── frontend/                # Streamlit：streamlit_app.py、ui_theme.py、agent_factory.py、views/
│   ├── config/
│   ├── data/
│   │   └── docs/                # 知识库 Markdown（ASCII 文件名，见下）
│   ├── rag/                     # RAG（rag_service.py、optimized_rag_service.py）
│   └── database/                # 连接与 mysql_init.sql
├── scripts/                     # 维护脚本（初始化/重置知识库）
├── tests/                       # 测试
│   └── performance/             # 并发与性能压测脚本
├── web/                         # React SPA（tech_stack_spec · Mock 阶段）
│   ├── README.md
│   ├── .env.example
│   └── src/                     # 路由、页面、Zustand、i18n、mocks
├── main.py
└── requirements.txt
```

`app/frontend/views/` 为 **st.Page 多页线稿骨架**（登录/注册、首页、文档库/详情、视频库/详情、智能问答、内容生成、任务中心、知识图谱、个人中心）。使用 `st.navigation` 后 Streamlit **不会**再自动读取 `pages/` 目录。登录为 **Mock**（任意用户名密码即可进入）。视频、任务队列、图谱、内容生成等无后端处为占位数据。线稿中的「底部全局导航」在 Streamlit 1.36 中无等价组件，已用 **左侧分组导航** 代替；页脚有简短说明。

知识库 `app/data/docs/` 中文档文件名示例：`faq.md`、`company_profile.md`、`business_process.md`、`products_services.md`（正文可为中文）。

## 快速开始

### 1. 环境准备

- Python 3.8+
- MySQL 5.7+
- MongoDB 4.0+
- PostgreSQL 14+（带 pgvector 扩展）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库初始化

#### MySQL
- 执行 `app/database/mysql_init.sql` 创建数据库和表

#### PostgreSQL
- 执行 `app/database/postgres_init.sql` 创建数据库和启用向量扩展

### 4. 配置修改

修改 `app/config/config.py` 中的配置信息：
- API密钥
- 数据库连接信息
- 模型配置

### 5. 启动应用（Streamlit 演示）

```bash
python main.py
```

应用将自动启动 Streamlit（默认入口 `app/frontend/streamlit_app.py`），访问 http://localhost:8501 即可使用。也可手动执行：

```bash
streamlit run app/frontend/streamlit_app.py
```

如需使用旧版单文件优化界面（未与线稿多页合并）：

```bash
streamlit run app/frontend/streamlit_app_lcp.py
```

### 5b. 文档知识库 API（FastAPI）与 Celery Worker

文档上传、解析、向量化、检索接口见规格 3.2。需已启动 PostgreSQL（pgvector）与 Redis。

```bash
# 终端 1：API（默认 http://127.0.0.1:8001）
uvicorn app.backend.api.main:app --host 0.0.0.0 --port 8001

# 终端 2：异步任务（与 compose 中 celery_worker 等价）
celery -A app.workers.celery_app worker --loglevel=info
```

- 宿主机连接 Docker 中的 Postgres 时，端口映射为 **5434**（见 `docker-compose.yml`），请设置环境变量 `POSTGRESQL_PORT=5434`；在容器内连 `postgres` 服务时使用 **5432**。
- 建表可执行 `scripts/migrations/001_kb_documents.sql`，或在首次请求 API 时由应用自动 `CREATE TABLE IF NOT EXISTS`。
- Streamlit「文档库」通过环境变量 `DOC_API_BASE_URL`（与 `config.KNOWLEDGE_BASE_CONFIG['api_base_url']` 一致）调用上述 API。无 Worker 时设置 `KB_DOC_SYNC_INGEST=true` 可在进程内同步解析/向量化（便于开发调试）。
- 使用本仓库 `docker compose up` 时，`docker-compose.yml` 已为 **streamlit** 服务设置 `DOC_API_BASE_URL=http://api:8001`，与 **api** 服务（内网 8001）对齐；宿主机访问文档 REST 请用 **http://localhost:8001**（已映射端口）。

### 5c. Docker Compose（精简）

```bash
docker compose up -d --build
```

- **Streamlit（经 Nginx）**：http://localhost  
- **文档知识库 API**：`http://localhost:8001`（路由见 `app/backend/api/routers/docs.py`，前缀为 `/docs/...`）。  
- 数据库端口：Postgres **5434**、MySQL **3307**、Redis **6379**、Mongo **27017**。

### 6. React 前端（推荐产品 UI，Mock 数据）

需 Node.js 18+ 与 npm。在 `python-ai-medical/web/` 下：

```bash
cd web
npm install
npm run dev
```

浏览器访问 **http://localhost:5173**。技术栈见 `Spec-coding/jishuzhan/tech_stack_spec.md` 与 `web/README.md`。  
与 Streamlit（端口 8501）可同时存在；后续接入 FastAPI 时，将 `web` 中 `src/lib/api.ts` 对接到真实 `/api` 即可。

### 7. 知识库维护脚本（可选）

在项目根目录 `python-ai-medical/` 下执行：

```bash
python scripts/init_knowledge_base.py
python scripts/reset_knowledge_base.py
```

## 核心功能使用

### 1. 医疗咨询
- 在聊天框中输入医疗相关问题
- 系统会基于大模型和知识库提供专业建议

### 2. 预约挂号
- 填写患者信息、科室、日期、时间等
- 点击"提交预约"按钮
- 系统会保存预约信息到数据库

### 3. 取消预约
- 填写预约时的信息
- 点击"取消预约"按钮
- 系统会删除对应的预约记录

### 4. 查询号源
- 选择科室、日期、时间
- 点击"查询"按钮
- 系统会返回号源情况

## 注意事项

1. 确保本地模型服务（http://10.204.220.21:8000/v1）可访问
2. 确保阿里云向量模型API密钥有效
3. 确保所有数据库服务正在运行
4. 首次启动时会自动加载知识库文档到向量存储

## 性能优化

- 使用连接池管理数据库连接
- 实现缓存机制减少重复计算
- 优化向量检索性能
- 使用异步处理提高响应速度

## 故障排查

1. **API连接失败**：检查网络连接和API密钥
2. **数据库连接失败**：检查数据库服务状态和连接配置
3. **模型调用失败**：检查模型服务是否正常运行
4. **知识库检索失败**：检查向量存储配置和文档加载

## 许可证

MIT
