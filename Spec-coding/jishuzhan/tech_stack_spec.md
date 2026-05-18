# 技术栈文档 — 智能知识库与多媒体 AI 平台

---

## 1️⃣ 后端技术栈

| 类别 | 技术/工具 | 说明 |
|------|-----------|------|
| **Web 框架** | FastAPI | 高性能、异步支持，自动生成 API 文档，适合 RAG + AI 查询接口 |
| **数据库** | PostgreSQL | 存储结构化数据，如用户、文档元信息、任务状态 |
| **向量化存储** | pgvector | 存储文档/视频文本向量，用于相似度检索 |
| **对象存储** | MinIO | 存储文档、视频、图片等大文件，S3 协议兼容 |
| **异步任务** | Celery + Redis | 支持文档解析、OCR、视频转写、AI 内容生成等后台任务 |
| **缓存** | Redis | 多轮问答缓存、任务状态缓存、常用向量缓存 |
| **AI 接口** | OpenAI GPT / 本地模型 / Whisper | 文本生成、问答、音频转写，可统一通过 AI 适配层调用 |
| **图数据库** | Neo4j | 知识图谱存储与可视化，支持关系查询和推荐系统 |
| **认证授权** | JWT + RBAC | 用户身份验证和角色权限控制 |
| **容器化** | Docker / Docker Compose | 后端服务容器化，便于部署与扩展 |
| **监控日志** | Prometheus + Grafana / ELK | 系统监控、任务监控、日志收集与可视化 |

### 数据流示意
1. 前端请求 → FastAPI 接口  
2. 异步任务（Celery）处理文档解析/视频转写 → MinIO / PostgreSQL / pgvector  
3. AI 问答接口调用 GPT / Whisper → 返回结果  
4. 缓存结果到 Redis，加速重复查询

---

## 2️⃣ 前端技术栈

| 类别 | 技术/工具 | 说明 |
|------|-----------|------|
| **框架** | React | 单页面应用（SPA），组件化开发 |
| **状态管理** | Zustand / Redux / Context API | 管理全局状态，如用户信息、问答历史、异步任务状态 |
| **UI 组件库** | shadcn/ui + Tailwind CSS | 低代码 UI 组件 + 实用的 Tailwind 样式快速布局 |
| **数据可视化** | Recharts / Chart.js / d3.js | 用于 Dashboard 图表、任务进度、推荐系统可视化 |
| **异步请求** | Axios / Fetch API | 调用 FastAPI 后端 REST 或 WebSocket 接口 |
| **路由** | React Router | 页面导航与多模块路由 |
| **富文本 / 编辑器** | react-quill / TipTap | 内容生成模块文本输入、笔记编辑 |
| **文件上传** | react-dropzone | 支持文档/视频拖拽上传 |
| **多媒体播放** | react-player | 视频播放，支持 mp4 / 网络视频链接 |
| **地图 / 图谱可视化** | Neo4j Bloom / d3.js | 企业知识图谱可视化 |
| **国际化 / 多语言** | i18next | 支持中文/英文等多语言显示 |
| **安全** | JWT token 存储（HttpOnly Cookie / localStorage） | 用户认证状态管理

### 前端页面设计思路
- 登录/注册 → Dashboard → 功能模块（文档、视频、问答、企业功能）
- 组件统一风格（Tailwind + shadcn/ui）
- 异步任务实时更新（轮询/ WebSocket）
- 数据可视化清晰、交互简单

