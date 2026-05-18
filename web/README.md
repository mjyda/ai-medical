# Web 前端（React / Mock）

技术栈对齐 `Spec-coding/jishuzhan/tech_stack_spec.md`：Vite、React、TypeScript、Tailwind CSS、shadcn/ui 风格组件、React Router、Zustand、Axios（预留）、Recharts、react-dropzone、react-player、TipTap、i18next。

## 命令

```bash
cd web
npm install
npm run dev
```

默认开发地址：http://localhost:5173

生产构建：

```bash
npm run build
npm run preview
```

## 环境变量（可选）

复制 `.env.example` 为 `.env`：

- `VITE_API_BASE`：API 根路径，默认 `/api`（Vite 已配置代理到 `http://127.0.0.1:8000`，待 FastAPI 就绪后启用）。

当前阶段数据为 **Mock**，无需后端即可浏览全部路由。

## 说明

- 已固定使用 **Vite 5** + `@vitejs/plugin-react@4`，避免 Vite 8 在部分环境下 `rolldown` 原生依赖缺失导致无法构建。
- 登录为 Mock：任意用户名密码或「跳过登录」；`auth_token` 写入 `localStorage` 供后续 Axios 拦截器演示。
