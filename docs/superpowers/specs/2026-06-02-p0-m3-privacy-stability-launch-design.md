# P0-M3 隐私、稳定、上线 — 设计说明（Spec）

> **状态：** 草案（基于 [p0-mvp-implementation.md](../../p0-mvp-implementation.md) §6 Phase 3、`main` @ M2 合并后差距分析）  
> **下一步：** [实施计划](../plans/2026-06-02-p0-m3-privacy-stability-launch.md)（`writing-plans`）

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
- `matched` 带简历证据摘录（可后续 API 扩展）
- PDF 高质量导出

## 工作包划分

| 包 | 名称 | 对应 Phase 3 | 依赖 |
|----|------|--------------|------|
| **M3-A** | 稳定与降级 | 3.3、3.4、3.5（部分） | 无 |
| **M3-B** | 隐私强化 + 本地 TTL | 3.1、3.2（本地） | 无 |
| **M3-C** | Cloudflare 持久化 | D1 + R2 替代内存存储 | M3-B 删除契约稳定 |
| **M3-D** | 部署与 Cron | 3.6、3.2（生产 24h） | M3-C |
| **M3-E** | 软上线验证 | 3.7 | M3-D |

**推荐顺序：** M3-A ∥ M3-B → M3-C → M3-D → M3-E  
（A/B 可并行；C 是 D 的前置。）

## 架构决策

### 存储抽象

- 引入 `SessionRepository` 接口（或 `Protocol`）：`create` / `get` / `update` / `patch_change` / `delete` / `store_file` / `get_file`。
- **P0 本地：** `InMemorySessionRepository`（现有 `session_store` 迁移）。
- **P0 生产：** `D1SessionRepository` + `R2BlobStore`（路径 `uploads/{session_id}/resume.docx`、`exports/{session_id}.docx`）。
- `main.py` 仅依赖仓库接口，通过 `SESSION_BACKEND=memory|cloudflare` 切换。

### 会话 API 扩展（降级）

| 场景 | 行为 |
|------|------|
| DOCX 解析失败或段落过少 | `POST /sessions` 接受可选 `resume_text`；跳过结构化解析，用 `raw_text` 走 Fact/LLM |
| LLM 超时/5xx | 已有 1 次重试；失败 → `status=failed`，`error` 含用户可读中文 + 建议重试 |
| 限流 | Worker 或 FastAPI 中间件：每 IP 每日 N 次 `POST /sessions`（默认 20，可 env 配置） |

### 隐私（3.1）

- 首页提交前 **必选勾选**「已阅读隐私说明并同意调用云模型处理简历与 JD」。
- 未勾选禁止提交（前端 + 可选后端 `consent=true` form 字段校验）。

### 自动删除（3.2）

| 环境 | 机制 |
|------|------|
| 本地 dev | `scripts/purge-expired-sessions.py` 或 uvicorn 启动说明；按 `created_at + AUTO_DELETE_HOURS` |
| 生产 | Worker **Cron** 每小时扫描 D1 `expires_at < now()`，删 D1 行 + R2 前缀；R2 lifecycle 规则作备份 |

与 [p0-cloudflare-stack.md](../../p0-cloudflare-stack.md) 一致：`AUTO_DELETE_HOURS` 默认 **24**。

### 部署（3.6）

```text
Pages (web) → Worker /api/* → Container (server) 
                ↘ D1 + R2
                ↘ Cron purge
```

- `NEXT_PUBLIC_API_BASE` 生产指向 Worker 同域 `/api`。
- Container 镜像 CI 构建；`wrangler d1 migrations apply` 纳入 CI（dry-run 或 preview）。

## 关键 UX

| 项 | 决策 |
|----|------|
| 解析失败 | 同页展示「粘贴简历全文」textarea，二次提交带 `resume_text` |
| 失败页 | `/s/[id]` `failed` 显示 `error` +「返回首页重试」 |
| 限流 | HTTP 429 + 文案「今日次数已用完，请明日再试」 |
| 删除 | 保留 M2 结果页按钮；生产删 D1+R2+导出 |

## 验证

| 层 | 命令 / 动作 |
|----|-------------|
| Server | `pytest`；新 repository / purge / rate-limit 测试 |
| Worker | `npm run typecheck`（若加 types 脚本）、wrangler 本地 dry-run |
| Web | `npm run build` |
| 人工 | §7.3 验收清单 + 生产 URL 走通上传→导出→删除 |
| 指标 | 种子用户 5–10 人 + 简单反馈表（Notion/表格） |

## 成功标准（M3 Done）

- [ ] 生产 URL 可完成 M2 人工验收清单
- [ ] 24h 后 Cron/脚本可清理测试会话（集成测或 staging 验证）
- [ ] 解析失败可用粘贴全文完成诊断（stub 或 real 至少一条 e2e）
- [ ] §9 隐私检查表 6 项均可勾选
- [ ] 限流在 staging 可触发 429
