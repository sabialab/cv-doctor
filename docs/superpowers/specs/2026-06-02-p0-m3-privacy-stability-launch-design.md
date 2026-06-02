# P0-M3 隐私、稳定、上线 — 设计说明（Spec）

> **状态：** 已批准（review clean @ 2026-06-02）  
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
| LLM `complete_json` 重试 1 次（`max_retries=1`） | ✅ |

## 非目标（本阶段不做）

- 用户账号 / 登录、付费墙完整实现（Phase 4）
- BOSS URL 抓取、公司画像 Target Mode（P1）
- Queues 异步诊断（P0.5，仅文档预留）
- `matched` 带简历证据摘录（`p0-mvp-implementation.md` §3.2 字面偏差；M3 不扩展 API）
- PDF 高质量导出、signed URL 导出（P0 用 R2 流式 download）

## 工作包划分

| 包 | 名称 | 对应 Phase 3 | 依赖 |
|----|------|--------------|------|
| **M3-A** | 稳定与降级 | 3.3、3.4、3.5 | — |
| **M3-B** | 隐私强化 + 本地 TTL | 3.1、3.2（本地） | Task 1 |
| **M3-C** | Cloudflare 持久化 | D1 + R2 | Task 1；Task 8；Task 8b 通过 |
| **M3-D** | 部署与 Cron | 3.6、3.2（生产） | M3-C |
| **M3-E** | 软上线验证 | 3.7 | M3-D |

**推荐顺序（与 plan Execution order 一致）：**

```text
Task 4, 4b ∥ Task 1 → Task 5 → Task 2, 3 → Task 6, 7 → Task 8 → 8b → 9a → 9b → 9c → 3b → 10, 11 → 12, 13
```

---

## 架构决策（已锁定）

### D1/R2 访问模型 — **方案 B（P0）**

| 组件 | 职责 |
|------|------|
| **Python Container** | `SessionRepository`：D1（REST/SQL API）+ R2（S3 兼容）；诊断 / PATCH / export |
| **Worker** | `/api/*` 代理；**Cron** TTL（D1 + R2 binding，与 Python 同库同 bucket） |
| **不采用方案 A** | 会话 CRUD 全在 Worker — 留 P1 |

**Task 8b spike（闸门）：** 见 `docs/notes/p0-m3-d1-r2-spike.md`；未通过则暂停 Task 9。

### 存储抽象

| 方法 / 字段 | 说明 |
|-------------|------|
| `create_session(..., resume_text?)` | `resume_bytes` 可为空 bytes（仅 `resume_text` 时） |
| `patch_change` / PolicyGuard | 与 M2 相同语义 |
| **memory** | `SessionRecord.export_path` 本地文件 |
| **cloudflare** | `resume_r2_key` / `export_r2_key` 列 + R2 对象 |
| R2 路径 | `uploads/{id}/resume.docx`、`exports/{id}/resume-export.docx` |

`SESSION_BACKEND=memory`（默认）| `cloudflare`（生产 Container）。

### 导出下载（已锁定）

| 环境 | 行为 |
|------|------|
| memory | `FileResponse(export_path)` |
| cloudflare | `GET /sessions/{id}/export/download` **从 R2 流式读取**（Task 9c） |

### 会话 API（降级 + 合规）

| 场景 | 行为 |
|------|------|
| 输入 | `resume`（.docx）与 `resume_text` **至少一项**；`jd_text` + **`consent=true`** 必填 |
| 解析失败 | `resume_text` → `Resume(raw_text=…)`；**real pipeline** 验收 |
| LLM 失败 | `failed` + 中文 `error`；`logger.exception` 仅服务端 |
| 限流 | **Staging/生产**（经 Worker）：`POST /api/sessions` + `CF-Connecting-IP`；**本地直连 Python**：`POST /sessions` + client host；**不同时**双层 |

### 隐私（3.1）与 §9 映射

| §9 项 | M3 任务 |
|-------|---------|
| 上传前告知云模型 | Task 5 + 现有首页/隐私文案 |
| 24h 删除 | Task 6（本地）、Task 10（Cron） |
| 一键删除 | Task 9c（D1 行 + R2 对象） |
| 不用于训练 | 已有隐私页 |
| JD 仅粘贴 | 已有 |
| 日志不落盘全文 | Task 4b |
| 免登录 | 已有 UUID session |

### 自动删除（3.2）

| 环境 | 机制 |
|------|------|
| 本地 | `scripts/purge-expired-sessions.py` + `AUTO_DELETE_HOURS=24` |
| 生产 | Worker Cron + R2 lifecycle 备份 |

### 部署与 staging

- **Staging：** 独立 `cv-doctor-p0-staging`（D1/R2/Worker/Pages）；**走 Worker `/api`**，可测 429 与 Cron。
- **生产 Container：** `USE_REAL_PIPELINE=1`、`DEEPSEEK_API_KEY`（禁止 stub 软上线）。
- `NEXT_PUBLIC_API_BASE` → 同域 `/api`。

---

## 关键 UX

| 项 | 决策 |
|----|------|
| 解析失败 | 首页粘贴全文；`FormData` 可仅 `resume_text` + `jd_text` + `consent` |
| 失败页 | `/s/[id]` `failed` |
| 限流 | 429 + 固定中文 `detail` |
| 删除 | 结果页 DELETE；清 D1 + 两路 R2 前缀 |

---

## 成功标准（M3 Done）

- [ ] Staging URL：M2 §7.3 人工验收清单
- [ ] TTL：staging Cron 或本地脚本删除过期会话
- [ ] `resume_text`：pytest（real pipeline 或 mock parser）或 runbook 人工步骤
- [ ] §9 上表七项均可勾选
- [ ] Staging 复现 429
- [ ] 生产 `USE_REAL_PIPELINE=1` smoke 通过
