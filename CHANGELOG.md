# Changelog

本文件记录 CV-Doctor（简历对症下药）仓库的重要变更，便于回溯产品与技术上下文。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### 计划中（P0 后续）

- Cloudflare 生产部署：D1 + R2 + Container + Cron TTL
- 持久化会话与 R2 简历存储
- Go–No-Go 指标与更多 fixture 场景

---

## [0.2.0-p0] — 2026-06-01

> Python 包版本（`server/pyproject.toml`）为 PEP 440 合规的 `0.2.0`；`web`/`worker` 的 npm 版本仍为 `0.2.0-p0`。

**Phase 1 诊断流水线**（[#2](https://github.com/sabialab/cv-doctor/pull/2) squash 合并至 `main`，`09fe8db`）。

### Added

- **真实流水线**（`USE_REAL_PIPELINE=1`）：DOCX 解析 → JD LLM 结构化 → 缺口分析 → 带 `evidence_ids` 的修改建议 → `PolicyGuard` → DOCX 导出
- `server/src/pipeline.py`、`parser_resume.py`、`parser_jd.py`、`facts.py`、`gap_analyzer.py`、`change_generator.py`、`llm/client.py`
- `exporter_docx.py`、`export_guard.py`；导出失败时若未匹配原文则 400
- 桩模式与真实模式均经 `apply_policy_guard`；桩修改含占位 `evidence_ids`
- **测试**：42 项 pytest（含 fixture 契约、export trust、LLM client mock）
- `docs/fixtures/sample-resume.docx`；Agent PR 工作流（`pr-workflow.mdc`、CLAUDE §5–8）

### Changed

- 默认 CI/本地仍为桩流水线（`USE_REAL_PIPELINE=0`）
- Worker 代理剥离 `content-encoding` / `content-length` 等易冲突头
- CI Web/Worker 统一 Node 22

### Security

- HIGH 风险修改不可导出；无 `evidence_ids` 的修改由 PolicyGuard 拦截
- LLM 日志不输出 ValidationError 原文（避免简历/JD 泄露）

---

## [0.1.0-p0] — 2026-06-01

首个可运行的 **P0 MVP 桩实现**（[#1](https://github.com/sabialab/cv-doctor/pull/1) squash 合并至 `main`，`b8ee7f9`）。

### Added

- **Server（FastAPI）**
  - `POST /sessions`：上传 `.docx` + 粘贴 JD，后台桩诊断
  - `GET /sessions/{id}`：轮询状态 `pending` | `processing` | `ready` | `failed`
  - `PATCH /sessions/{id}/changes/{id}`：采纳/拒绝修改建议（`session_store` 锁内更新）
  - `POST /sessions/{id}/export`：导出已采纳修改为 `.txt`（桩）
  - `DELETE /sessions/{id}`：删除会话与导出文件
  - `p0_models.py`、`api/schemas.py`、`stub_pipeline.py`、内存 `SessionStore`
  - `server/tests/test_api.py`（20 项）
  - `server/Dockerfile`（面向 Cloudflare Container 目标）
- **Web（Next.js App Router）**
  - `/`：上传简历 + JD
  - `/s/[id]`：轮询结果；JD 解读 → 匹配分 → 缺口 → 修改建议；高风险二次确认后采纳；导出/删除
  - `/privacy`：隐私与保留说明
  - `web/lib/api.ts`：与后端契约对齐（`ready` 非 `done`）
- **Worker（Hono + Wrangler）**
  - `/api/*` 代理至 `PIPELINE_URL`；查询串经 `URL.search` 转发
  - `worker/wrangler.toml` 与本地 `npm run dev`
- **文档**
  - `docs/p0-cloudflare-stack.md`：全 Cloudflare 目标架构
  - `docs/fixtures/sample-jd.txt`、fixtures README
  - `docs/architecture.md` §1.5 文档/Agent 索引
  - Agent 规范：`CLAUDE.md`、`AGENTS.md`、`.cursor/rules/*`（含 `worker-edge`）
- **CI**（`.github/workflows/ci.yml`）
  - 并行：Server（Ruff 限定 P0 路径 + pytest）、Web build、Worker tsc + wrangler dry-run
  - Node **22**（Wrangler 4.x 要求）；`permissions: contents: read`

### Changed

- `docs/p0-mvp-implementation.md`：会话终态文档与实现对齐为 `ready`（非 `done`）
- `README.md`：P0 本地运行与文档链接

### Security / 信任边界

- 前端：高风险 / `requires_user_confirmation` 修改需两步确认后才能采纳
- 桩流水线：不编造简历事实；缺口仅作建议展示（完整 `PolicyGuard` 待真实 LLM 管线接入）

### 已知限制（本版本）

- 诊断为 **桩数据**，非真实 DOCX/LLM
- 会话 **进程内内存**，重启丢失
- 导出为 **`.txt`**，非 DOCX
- 未部署 Cloudflare 生产栈（D1/R2/Cron 为文档目标）

---

## [0.0.2] — 2026-05（规划与文档）

### Added

- `docs/p0-mvp-implementation.md`：P0 范围、API 契约、验收与里程碑
- `docs/mvp-feasibility.md`：可行性分析
- `docs/architecture.md`：逻辑架构与 Pipeline 说明
- `CLAUDE.md` / `AGENTS.md`：Agent 执行标准（Karpathy 准则 + P0 护栏）
- `623d50b`：P0 MVP 计划与架构文档入库

### Changed

- `PLAN.md`：v2 → v3.x（Web/H5 优先、LLM 分工、中国市场竞品与打法）

---

## [0.0.1] — 2026-05

### Added

- 项目初始化（`904e1f8`）：`PLAN.md`、基础目录与长期领域模型骨架（`server/src/models.py` 等）

---

[0.2.0-p0]: https://github.com/sabialab/cv-doctor/compare/b8ee7f9...09fe8db
[0.1.0-p0]: https://github.com/sabialab/cv-doctor/compare/623d50b...b8ee7f9
[0.0.2]: https://github.com/sabialab/cv-doctor/compare/904e1f8...623d50b
[0.0.1]: https://github.com/sabialab/cv-doctor/commit/904e1f8
