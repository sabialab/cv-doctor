# P0 全 Cloudflare 部署架构

> 你有 Workers 订阅；P0 前后端与存储均落在 Cloudflare，不再依赖 Vercel 第二套免费额度或单独 VPS 跑公网 API。

最后更新：2026-06-01

---

## 1. 组件映射

| 能力 | Cloudflare 产品 | 仓库路径 |
|------|-----------------|----------|
| 前端 Next.js | **Pages**（OpenNext / `@opennextjs/cloudflare`） | `web/` |
| 边缘 API（会话、上传、CORS） | **Worker**（Hono） | `worker/` |
| 简历/JD 流水线（python-docx、LiteLLM） | **Containers**（Docker 镜像 = `server/`） | `server/` |
| 原始 DOCX / 导出文件 | **R2** | 绑定 `UPLOADS` |
| 会话元数据（状态、过期时间） | **D1**（SQLite） | 绑定 `DB` |
| 24h 清理 | **Cron Trigger**（Worker） | `worker/` |
| 长耗时诊断（可选 P0.5） | **Queues** | Worker → Container |

---

## 2. 请求路径（P0）

```text
浏览器 (Pages)
  → Worker API (HTTPS, 同域或 api.子域)
       → 写 R2：uploads/{session_id}/resume.docx
       → 写 D1：sessions 行（status=pending）
       → 同步调用 Container / 或 Queue 投递后轮询
            → Python：解析 DOCX、JD 抽取、LLM、PolicyGuard
       → 读 D1 + R2，返回 DiagnosisResult JSON
  → 结果页 /s/[id] 轮询 GET /sessions/{id} 直至 status=ready
```

**为何保留 Python 容器：** 现有 `server/src/models.py` 与后续 `python-docx` 逻辑已在 Python；在 Worker 里重写成本过高。Container 与 Worker 同属 Cloudflare 账单，仍算「全 CF」。

**45 秒 LLM：** Worker 单次请求 CPU 有限；P0 采用 **异步诊断 + 轮询**（`POST` 返回 `session_id`，`GET` 查状态），避免在边缘 Worker 内同步阻塞 45s。本地开发时 Python `server` 可继续同步跑通。

---

## 3. 环境变量（示例）

| 变量 | 设置位置 | 说明 |
|------|----------|------|
| `DEEPSEEK_API_KEY` | Container secret / `wrangler secret` | 仅流水线容器可读 |
| `AUTO_DELETE_HOURS` | Worker + Container | 默认 `24` |
| `PIPELINE_URL` | Worker var | 容器内网 URL 或 service binding |
| `ALLOWED_ORIGINS` | Worker var | Pages 预览/生产域名 |

---

## 4. 本地开发

```bash
# 终端 1：Python API（与容器内代码相同）
cd server && uv sync && uv run uvicorn src.main:app --reload --port 8787

# 终端 2：Worker（代理到本地 Python，可选）
cd worker && npm i && npm run dev

# 终端 3：Next.js
cd web && npm i && npm run dev
```

`web` 通过 `NEXT_PUBLIC_API_BASE` 指向 `http://127.0.0.1:8787`（本地）或 Worker 预览 URL。

---

## 5. 与 `docs/p0-mvp-implementation.md` 的关系

- 产品范围、API 契约、验收指标：**不变**（仍以 P0 文档为准）。
- §8 部署：以 **本文** 为准，替代原「Vercel + VPS」示意图。
- Postgres/Redis：**P0 不用**；D1 + R2 足够。

---

## 6. 上线检查（CF 特有）

- [ ] R2 生命周期规则：前缀 `sessions/` 与 `AUTO_DELETE_HOURS` 一致
- [ ] D1 迁移脚本纳入 CI（`wrangler d1 migrations apply`）
- [ ] Container 镜像在 `wrangler deploy` 流水线构建
- [ ] Pages 环境变量 `NEXT_PUBLIC_API_BASE` 指向生产 Worker
- [ ] CORS `ALLOWED_ORIGINS` 仅含 Pages 域名
