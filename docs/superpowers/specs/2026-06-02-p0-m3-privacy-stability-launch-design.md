# P0-M3 隐私、稳定、上线 — 设计说明（Spec）

> **状态：** 已批准（2026-06-02 review 修订）  
> **实施计划：** [2026-06-02-p0-m3-privacy-stability-launch.md](../plans/2026-06-02-p0-m3-privacy-stability-launch.md)

## Goal

**里程碑 M3：** 对外软上线 — 公网可访问、数据可删可过期、解析/LLM 失败可降级、基础防刷，满足 §9 隐私检查表，开始收集 Go/No-Go 指标。

## 已完成（M2 / `main`）

| 能力 | 状态 |
|------|------|
| 浏览器闭环（上传 → 进度 → 五段式 → diff → DOCX） | ✅ |
| `DELETE /sessions/{id}` + 导出文件清理 | ✅ 内存 `SessionStore` |
| 首页/隐私 DeepSeek、保留期文案（本地 vs 生产 24h） | ✅ |
| `USE_REAL_PIPELINE=1` 真实管线 | ✅ |
| Worker `/api/*` 代理骨架 | ✅ 无 D1/R2 |
| LLM `complete_json` 重试 1 次 | ✅ `llm/client.py` |

## 非目标（本阶段不做）

- 用户账号 / 登录、付费墙完整实现（Phase 4）
- BOSS URL 抓取、公司画像 Target Mode（P1）
- Queues 异步诊断（P0.5，仅文档预留）
- `matched` 带简历证据摘录（与 `p0-mvp-implementation.md` §3.2 字面略有偏差；M3 不扩展 API）
- PDF 高质量导出

## 工作包划分

| 包 | 名称 | 对应 Phase 3 | 依赖 |
|----|------|--------------|------|
| **M3-A** | 稳定与降级 | 3.3、3.4、3.5 | 无 |
| **M3-B** | 隐私强化 + 本地 TTL | 3.1、3.2（本地） | Task 1（Repository） |
| **M3-C** | Cloudflare 持久化 | D1 + R2 | Task 1；Task 8 spike |
| **M3-D** | 部署与 Cron | 3.6、3.2（生产） | M3-C |
| **M3-E** | 软上线验证 | 3.7 | M3-D |

**推荐顺序：** Task 4 ∥ Task 1 → Task 2–3 → M3-B → Task 8 → Task 9 → M3-D → M3-E

---

## 架构决策（已锁定）

### D1/R2 访问模型 — **方案 B（P0）**

| 组件 | 职责 |
|------|------|
| **Python Container** (`server/`) | `SessionRepository` 实现：D1 REST/SQLite API + R2 S3 兼容 API；诊断、PATCH、export 业务逻辑不变 |
| **Worker** (`worker/`) | `/api/*` 反向代理到 Container；**Cron** 用原生 D1/R2 binding 做 TTL 清理（与 Python 共享同一 D1 表与 bucket） |
| **不采用方案 A** | 会话 CRUD 全部搬进 Worker、Container 无状态 — 改动面过大，留 P1 |

**Task 8 spike（0.5d）：** 在合并 Task 9 前，验证 Container 环境能读写一条 D1 行 + R2 对象（或文档记录所需 env：`CLOUDFLARE_*` / service token）。

### 存储抽象

`SessionRepository` 方法（与 M2 行为一致）：

- `create_session(resume_bytes, jd_text, resume_text?)`
- `get_session` / `update_session` / `patch_change` / `delete_session`
- R2 keys：`uploads/{session_id}/resume.docx`、`exports/{session_id}/resume-export.docx`
- `put_resume_bytes` / `put_export_docx` / `open_export_read` / `delete_session_files`

`SESSION_BACKEND=memory`（默认）| `cloudflare`（生产 Container）。

### 导出下载（生产）

| 环境 | 行为 |
|------|------|
| 本地 memory | 保持 `FileResponse(export_path)` |
| 生产 R2 | `GET .../export/download` 从 R2 流式读取；或 `POST /export` 返回短期 signed URL（二选一，计划 Task 9c 锁定） |

### 会话 API 扩展（降级）

| 场景 | 行为 |
|------|------|
| 输入 | **`resume`（.docx）与 `resume_text` 至少一项**；禁止「无文件无文本」 |
| DOCX 解析失败或段落过少 | 若有 `resume_text`，构建 `Resume(raw_text=…)` 走 real pipeline；stub 仅用于结构测试 |
| LLM 失败 | `status=failed`，`error` 为用户可读中文（无堆栈）；服务端 `logger.exception` |
| 限流 | **生产：** Worker 对 `POST /api/sessions` 按 `CF-Connecting-IP` 日限 N；**本地：** FastAPI 对 `POST /sessions` 按 client host；**不同时** 叠两层 |

Worker 代理须透传客户端 headers（已有 `headers` 克隆）；限流在 **Worker 边缘**读取 `CF-Connecting-IP`，不依赖 Container 解析 IP（Task 3/11 验收）。

### 隐私（3.1）

- 首页必选勾选同意；`consent=true` form 字段；后端 400 若缺失。

### 自动删除（3.2）

| 环境 | 机制 |
|------|------|
| 本地 | `scripts/purge-expired-sessions.py` + `AUTO_DELETE_HOURS`（默认 24） |
| 生产 | Worker Cron + R2 lifecycle 备份；`expires_at` 在 create 时写入 D1 |

### 部署（3.6）与 staging

- **Staging：** Cloudflare Pages preview 或固定 `staging.*` 子域 + 独立 Worker/D1/R2 名（`cv-doctor-p0-staging`）；与生产密钥隔离。
- **生产 Container 必设：** `USE_REAL_PIPELINE=1`、`DEEPSEEK_API_KEY`；禁止软上线仍跑 stub。
- `NEXT_PUBLIC_API_BASE` → 同域 `/api`；`ALLOWED_ORIGINS` 仅 Pages 域。

### 可观测性与 §9

- 请求日志：`session_id` + 路径；**禁止**记录 `jd_text` / 简历正文 / `revised` 全文（Task 4b）。

---

## 关键 UX

| 项 | 决策 |
|----|------|
| 解析失败 | 首页展示「粘贴简历全文」；`resume_text` + 可选仍传 docx |
| 失败页 | `/s/[id]` `failed` + 返回首页 |
| 限流 | 429 +「今日诊断次数已达上限，请明日再试」 |
| 删除 | M2 按钮；生产删 D1 行 + R2 `uploads/` + `exports/` 前缀 |

---

## 验证

| 层 | 动作 |
|----|------|
| Server | `pytest`；`memory` / `cloudflare`（mock）参数化 `test_api*.py` |
| Worker | `wrangler deploy --dry-run`；Cron 手动触发 |
| Web | `npm run build` |
| 人工 | §7.3 + staging URL |
| 指标 | 5–10 种子用户 |

## 成功标准（M3 Done）

- [ ] Staging/production URL 完成 M2 人工验收清单
- [ ] TTL：脚本或 Cron 在 staging 删除过期会话
- [ ] `resume_text` e2e（**real pipeline**）至少 1 条 pytest 或文档化人工步骤
- [ ] §9 六项（含日志不落盘全文）
- [ ] Staging 可复现 429
- [ ] 生产 `USE_REAL_PIPELINE=1` 已配置并 smoke 通过
