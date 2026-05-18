# Spec Coding 文档 — 智能知识库与多媒体 AI 平台

---

## 1️⃣ 项目概述
- **项目名称**：智能知识库与多媒体 AI 平台  
- **目标用户**：企业团队、个人学习者  
- **核心功能**：
  1. 文档上传、解析与向量化  
  2. AI 问答与多轮对话  
  3. 视频下载、转写与内容生成  
  4. 企业级功能：RBAC、订阅、知识图谱、推荐系统  
- **技术栈**：
  - 后端：FastAPI  
  - 前端：React  
  - 数据库：PostgreSQL + pgvector  
  - 对象存储：MinIO  
  - 异步任务：Celery + Redis  
  - AI 模型：Whisper / GPT 系列  
  - 图数据库：Neo4j  

---

## 2️⃣ 功能模块及需求

### 2.1 文档知识库模块
- **功能描述**：
  - 上传 PDF/DOCX 文档（支持批量上传）  
  - OCR 支持扫描版 PDF  
  - 文档解析 → 向量化 → 存储  

- **约束与非功能需求**：
  - 文件大小限制：≤ 100MB  
  - 支持多语言文本向量化  
  - 异步任务处理（Celery）  

---

### 2.2 AI 问答模块
- **功能描述**：
  - 基于 RAG 流程进行问答  
  - 支持多轮对话和历史记录展示  
  - 缓存机制与失败重试  

- **约束与非功能需求**：
  - 缓存策略：Redis  
  - 向量化接口统一（与文档模块保持一致）  
  - 查询响应时间 ≤ 3s  

---

### 2.3 视频处理模块
- **功能描述**：
  - 下载视频（YouTube/Bilibili/TikTok）  
  - 音频提取与转写（Whisper）  
  - 文本切片 + 向量化  
  - AI 内容生成（模板化 prompt）  

- **约束与非功能需求**：
  - 异步任务队列（Celery）  
  - 支持任务状态查询、失败重试  
  - 确保版权/合规提示  

---

### 2.4 企业级功能模块
- **功能描述**：
  - 用户角色与订阅管理（RBAC）  
  - AI 适配层（支持国内/国外模型 Mock）  
  - 知识图谱（Neo4j schema）  
  - 推荐系统（规则/简单图遍历）  
  - Dashboard 数据异步加载  

- **约束与非功能需求**：
  - Neo4j schema 需提前设计  
  - Mock 接口减少外部依赖  
  - Dashboard 异步加载避免性能瓶颈  

---

## 3️⃣ 接口文档 / API

### 3.1 用户管理接口
| 接口 | 方法 | 参数 | 返回 | 异常 |
|------|------|------|------|------|
| /auth/register | POST | username, password, email | user_id, status | 400 用户名重复 |
| /auth/login | POST | username, password | token, user info | 401 未授权 |
| /auth/roles | GET | user_id | list[roles] | 404 用户不存在 |

---

### 3.2 文档管理接口
| 接口 | 方法 | 参数 | 返回 | 异常 |
|------|------|------|------|------|
| /docs/upload | POST | file | doc_id, status | 413 文件过大 |
| /docs/parse | POST | doc_id | parsed_text | 404 文档不存在 |
| /docs/vectorize | POST | doc_id | vector_id | 404 文档不存在 |
| /docs/search | POST | query | list[doc_id, snippet, score] | 500 AI 错误 |

---

### 3.3 AI 问答接口
| 接口 | 方法 | 参数 | 返回 | 异常 |
|------|------|------|------|------|
| /qa/query | POST | query, history | answer, source | 500 AI 服务异常 |
| /qa/history | GET | user_id | list[query, answer, timestamp] | 404 用户不存在 |

---

### 3.4 视频处理接口
| 接口 | 方法 | 参数 | 返回 | 异常 |
|------|------|------|------|------|
| /videos/download | POST | url | video_id, path | 400 URL 不合法 |
| /videos/transcribe | POST | video_id | transcript_id | 404 视频未找到 |
| /videos/vectorize | POST | transcript_id | vector_id | 404 转写未找到 |
| /videos/generate | POST | prompt, template | generated_content | 500 AI 错误 |

---

### 3.5 企业功能接口
| 接口 | 方法 | 参数 | 返回 | 异常 |
|------|------|------|------|------|
| /enterprise/roles | GET | user_id | list[roles] | 404 用户不存在 |
| /enterprise/recommend | GET | user_id | list[item_id] | 500 内部错误 |
| /enterprise/graph | GET | query | list[node/relationship] | 500 Neo4j 错误 |

---

## 4️⃣ 架构设计图
![系统架构 / 数据流 / 模块依赖图](./a_large_infographic_system_architecture_diagram.png)

---

## 5️⃣ 测试用例 / QA

### 5.1 用户管理
| 功能 | 测试场景 | 输入 | 期望输出 |
|------|---------|------|----------|
| 登录 | 正常 | username/password | token + user info |
| 登录 | 密码错误 | username/wrongpwd | 401 错误 |
| 注册 | 用户名重复 | username | 400 错误 |

### 5.2 文档管理
| 功能 | 测试场景 | 输入 | 期望输出 |
|------|---------|------|----------|
| 上传 | 文件合法 | PDF/DOCX | doc_id |
| 上传 | 文件过大 | >100MB | 413 错误 |
| 向量化 | 文档存在 | doc_id | vector_id |
| 向量化 | 文档不存在 | doc_id | 404 错误 |

### 5.3 AI 问答
| 功能 | 测试场景 | 输入 | 期望输出 |
|------|---------|------|----------|
| 查询 | 有文档匹配 | query | answer + source |
| 查询 | 无匹配 | query | 空结果或提示 |

### 5.4 视频处理
| 功能 | 测试场景 | 输入 | 期望输出 |
|------|---------|------|----------|
| 下载 | URL 合法 | 视频 URL | video_id/path |
| 下载 | URL 不合法 | bad URL | 400 错误 |
| 转写 | 视频存在 | video_id | transcript_id |
| 转写 | 视频不存在 | video_id | 404 错误 |

### 5.5 企业功能
| 功能 | 测试场景 | 输入 | 期望输出 |
|------|---------|------|----------|
| RBAC | 查询用户角色 | user_id | list[roles] |
| 推荐 | 有数据 | user_id | list[item_id] |
| 推荐 | 无数据 | user_id | 空列表 |

---

💡 **补充说明**
- 异步任务（Celery）需要保证失败重试策略和状态更新  
- 缓存策略（Redis）用于加速 AI 查询和文档搜索  
- OCR 与向量化接口需与文档模块统一  
- AI 内容生成需支持模板化 prompt

