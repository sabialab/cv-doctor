# P0-M3 Privacy, Stability & Launch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Soft-launch P0 on Cloudflare — persistent sessions (D1/R2), 24h auto-delete, parse/LLM degradation, rate limits, upload consent, production deploy.

**Architecture:** `SessionRepository` + **方案 B**（Python 持 D1/R2 业务读写，Worker 代理 + Cron）。详见 spec。

**Tech Stack:** FastAPI, D1, R2 (S3 API), Wrangler, Hono Worker, Next.js 15, pytest.

**Spec:** [docs/superpowers/specs/2026-06-02-p0-m3-privacy-stability-launch-design.md](../specs/2026-06-02-p0-m3-privacy-stability-launch-design.md)

**Branch:** `feat/p0-m3-launch` from `origin/main`

**Plan revisions:** 2026-06-02 r1–r8；r4–8 = review/autofix 至 CLEAN。

**Review status:** CLEAN（2026-06-02，见文末 Review log）

---

## Execution order (locked)

```text
Task 4, 4b  (errors, logging)              ∥  Task 1 (repository)
        → Task 5 (consent)                  ← 必须先于 Task 2（API 要求 consent）
        → Task 2, 3 (resume_text, rate limit)
        → Task 6, 7 (purge, paste UI)       [7 after 2]
        → Task 8 → 8b (spike) → 9a → 9b → 9c
        → Task 3b (memory；9c 后加 cloudflare)
        → Task 10, 11 (cron, runbook)
        → Task 12, 13
```

---

## File structure (target)

| Path | Responsibility |
|------|----------------|
| `server/src/repositories/session.py` | Protocol + `get_repository()` |
| `server/src/repositories/memory.py` | In-memory；`export_path` |
| `server/src/repositories/r2_store.py` | R2 put/get/delete |
| `server/src/repositories/d1_store.py` | D1 rows + JSON |
| `server/src/repositories/cloudflare.py` | Composes d1 + r2 |
| `server/src/services/rate_limit.py` | Local only |
| `worker/src/rate_limit.ts` | `POST /api/sessions` only |
| `worker/src/cron_purge.ts` | TTL |
| `worker/src/index.ts` | Wire cron + rate limit |
| `worker/migrations/0001_sessions.sql` | Schema |
| `scripts/purge-expired-sessions.py` | Local TTL |
| `docs/notes/p0-m3-d1-r2-spike.md` | Task 8b 输出（Task 11 可摘录） |
| `docs/deploy-p0-m3.md` | Task 11 主文档 |
| `docs/seed-user-feedback-template.md` | Task 13 |

---

## M3-A — Stability & degradation

### Task 1: `SessionRepository` + memory migration

**Depends on:** —

**Files:** `server/src/repositories/{session,memory}.py`, `server/src/services/session_store.py`（shim）, `server/src/main.py`, `server/tests/*`

- [ ] Protocol：`create_session(resume_bytes, jd_text, resume_text?)`；`patch_change` → `PatchChangeResult`；文件 helpers。
- [ ] `memory.py`：迁移 `session_store`；保留 `export_path` + `EXPORT_DIR` 行为。
- [ ] `get_repository()`：`SESSION_BACKEND=memory|cloudflare`。
- [ ] `pytest -q` → commit `refactor(server): SessionRepository and memory backend`

---

### Task 4: User-facing pipeline errors

**Depends on:** —（∥ Task 1）

**Files:** `server/src/main.py`, `server/tests/test_api_failed_session.py`

- [ ] Test：`failed` + 中文 `error`，无 `Traceback`。
- [ ] `LLMError` / `ValidationError` / 兜底文案；`logger.exception`。
- [ ] Commit `fix(api): friendly failed-session errors`

---

### Task 4b: Log redaction (§9)

**Depends on:** Task 4

**Files:** `server/src/logging_config.py`（或 `main.py`）, `server/tests/test_logging_redaction.py`

- [ ] 禁止日志打印完整 `jd_text`、简历 bytes、`revised`。
- [ ] 在 `docs/deploy-p0-m3.md` §Operations 记一笔（Task 11 创建文件后补全或先写 `docs/notes/...`）。
- [ ] Commit `fix(ops): redact PII from server logs`

---

### Task 5: Upload consent

**Depends on:** —（**必须在 Task 2 之前合并**）

**Files:** `web/app/page.tsx`, `web/lib/api.ts`, `server/src/main.py`, `server/tests/test_api.py`

- [ ] 首页必选勾选；`consent=true`。
- [ ] `POST /sessions` 无 consent → 400。
- [ ] Commit `feat: require privacy consent on session create`

---

### Task 2: `POST /sessions` resume text fallback

**Depends on:** Task 1, **Task 5**

**Files:** `server/src/main.py`, `server/src/pipeline.py`, `server/tests/test_api_resume_text_fallback.py`

**API contract (locked):**

| Field | Rule |
|-------|------|
| `resume` | 可选 `.docx` |
| `resume_text` | 可选 |
| | 至少一项 |
| `jd_text`, `consent` | 必填 |

- [ ] Test：`resume_text` only + `USE_REAL_PIPELINE=1`（或 mock parser 失败）→ `ready`。
- [ ] `_run_diagnosis`：空解析时用 `resume_text` 构建 `Resume`；仅文本时 `resume_bytes=b""` 入库/R2。
- [ ] Commit `feat(api): resume_text fallback`

---

### Task 3: Rate limit

**Depends on:** Task 1

**Files:** `server/src/services/rate_limit.py`, `worker/src/rate_limit.ts`, `worker/src/index.ts`, `server/tests/test_rate_limit.py`, `web/lib/api.ts`

- [ ] **本地：** FastAPI `POST /sessions`；`RATE_LIMIT_SESSIONS_PER_DAY=20`。
- [ ] **Worker：** 仅匹配 `POST /api/sessions`；`CF-Connecting-IP`（fallback 首段 `X-Forwarded-For`）；429 `detail` 与 spec 一致。
- [ ] **Staging** 经 Worker → 可测 429（Task 12）。
- [ ] Commit `feat: rate limit session create (local + edge)`

---

### Task 3b: Parametrized API tests

**Depends on:** Task 1；cloudflare 用例在 **Task 9c 后**追加

**Files:** `server/tests/conftest.py`, `test_api.py`, `test_api_patch_change.py`

- [ ] `@pytest.mark.parametrize("backend", ["memory"])` 跑通现有 API 测试。
- [ ] 9c 后增加 `"cloudflare"` + mocks。
- [ ] Commit `test: parametrize session API by backend`

---

## M3-B — Privacy & local TTL

### Task 6: Local TTL purge

**Depends on:** Task 1

**Files:** `scripts/purge-expired-sessions.py`, `memory.py`, `server/tests/test_purge_expired.py`, `server/.env.example`

- [ ] `list_expired(before)` + 删 export 文件。
- [ ] Commit `feat(ops): purge expired local sessions`

---

### Task 7: Frontend parse-fallback UI

**Depends on:** Task 2

**Files:** `web/app/page.tsx`, `web/lib/api.ts`

- [ ] `createSession`：`FormData` 支持无文件、仅 `resume_text`。
- [ ] 解析类错误展示粘贴区并重试。
- [ ] Commit `feat(web): resume text fallback UI`

---

## M3-C — Cloudflare persistence

### Task 8: D1 schema

**Depends on:** Task 1

**Files:** `worker/migrations/0001_sessions.sql`, `worker/wrangler.toml`

```sql
CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  jd_text TEXT NOT NULL,
  result_json TEXT,
  error TEXT,
  processing_step TEXT,
  resume_r2_key TEXT,
  export_r2_key TEXT
);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
```

- [ ] Commit `feat(worker): D1 sessions schema`

---

### Task 8b: D1/R2 spike（闸门）

**Depends on:** Task 8

**Files:** `docs/notes/p0-m3-d1-r2-spike.md`

- [ ] 记录 Container 读写 D1/R2 的步骤、env、结果或 blocker。
- [ ] **失败则停止 Task 9**；不合并未验证的 `cloudflare` backend。

---

### Task 9a: R2 file store

**Depends on:** Task 8b 通过

**Files:** `server/src/repositories/r2_store.py`, tests

- [ ] put/get/delete；路径与 spec 一致。

---

### Task 9b: D1 metadata store

**Depends on:** Task 8b 通过

**Files:** `server/src/repositories/d1_store.py`, tests

- [ ] CRUD + `result_json`；`expires_at` from `AUTO_DELETE_HOURS`。

---

### Task 9c: Cloudflare repository + export + delete

**Depends on:** 9a, 9b, Task 1

**Files:** `cloudflare.py`, `main.py` download route, tests

- [ ] `SESSION_BACKEND=cloudflare`。
- [ ] Export：`GET .../export/download` R2 流式（**不用** signed URL）。
- [ ] PATCH：清 `export_r2_key` + 删 R2 export 对象（同 M2 `export_path`）。
- [ ] `DELETE`：删 D1 行 + `uploads/{id}/` + `exports/{id}/` 下对象。
- [ ] 完成 Task 3b cloudflare 参数。
- [ ] Commit `feat(server): cloudflare session repository`

---

## M3-D — Deploy & Cron

### Task 10: Worker Cron purge

**Depends on:** Task 8, 9a, 9b（D1 行 + R2 路径约定）

**Files:** `worker/src/cron_purge.ts`, `worker/src/index.ts`, `worker/wrangler.toml`

- [ ] SQL `expires_at < now()`；R2 `list` + `delete` per `session_id`（非 glob `/*`）。
- [ ] `triggers.crons = ["0 * * * *"]`
- [ ] Commit `feat(worker): cron purge expired sessions`

---

### Task 11: Deploy runbook

**Depends on:** —（可与 Task 10 并行；吸收 8b spike 节）

**Files:** `docs/deploy-p0-m3.md`, optional `.github/workflows/ci.yml`

| Section | Content |
|---------|---------|
| Staging | `cv-doctor-p0-staging`；Worker 路径；429 测试 |
| Production | `USE_REAL_PIPELINE=1`, secrets, Pages, Container |
| Spike | 摘自 `docs/notes/p0-m3-d1-r2-spike.md` |
| §7.3 | 人工验收清单 |
| Ops | Task 4b 日志脱敏 |

- [ ] Commit `docs: P0-M3 deploy runbook`

---

## M3-E — Validation

### Task 12: E2E verification

- [ ] Local：`pytest`, `npm run build`, stub + real smoke。
- [ ] Staging：§7.3 + TTL + 429 + delete。
- [ ] `cr review --base main --plain`
- [ ] Squash merge `feat/p0-m3-launch`

---

### Task 13: Seed users

**Files:** `docs/seed-user-feedback-template.md`

- [ ] 5–10 人；Go/No-Go 对照 `p0-mvp-implementation.md` §1.3。

---

## Verification commands

```bash
cd server && uv sync --extra dev --frozen && uv run ruff check src/ tests/ && uv run pytest -q
cd web && npm ci && npm run build
cd worker && npm ci && npx wrangler deploy --dry-run
```

---

## Risk register

| 风险 | 对策 |
|------|------|
| D1/R2 ≠ memory | Task 3b |
| consent 晚于 resume API | Task 5 在 Task 2 前（execution order） |
| 8b 失败 | 闸门；不合并 9 |
| Staging 未走 Worker | runbook 强制 staging 经 `/api` |
| Cron R2 列表遗漏 | 按 `session_id` 前缀 list |

---

## Doc updates

- [x] `p0-mvp-implementation.md` — Phase 3 → 本 plan
- [x] `architecture.md` — M3 当前
- [ ] `README.md` — 生产 URL（Task 11）

---

## Summary

| 包 | 交付 |
|----|------|
| M3-A | Repository、降级、限流、错误、日志 |
| M3-B | consent、purge、粘贴 UI |
| M3-C | D1/R2、导出、DELETE |
| M3-D | Cron、runbook |
| M3-E | Staging 验收、种子用户 |

---

## Review log

| Round | 发现 | 处理 |
|-------|------|------|
| 1–3 | （见历史） | 方案 B、9 拆分、限流分层… |
| 4 | Task 2 要求 consent 但 Task 5 在后 | Execution：Task 5 → Task 2 |
| 4 | 导出「二选一」未锁定 | Spec/plan：仅 R2 流式 download |
| 4 | 8b/4b 与 Task 11 争用 deploy 文档 | 8b → `docs/notes/p0-m3-d1-r2-spike.md` |
| 4 | DELETE 生产路径未写 | Task 9c 补 D1+R2 删除 |
| 5 | Spec 推荐顺序与 plan 不一致 | 统一为 Execution order 块 |
| 5 | §9 六项未映射任务 | Spec 表 + Task 5/6/10/9c/4b |
| 5 | Staging 429 含糊 | Staging 必须经 Worker `/api` |
| 6 | Task 7/10 缺 Files/Depends | 已补 |
| 6 | memory 仍用 `export_path` | Task 1 明确 |
| 6 | Cron `/*` 非 R2 API | Task 10 list+delete |
| 7 | Task 10 早于 9a 会删不掉 R2 | Depends 含 9a |
| 8 | 仅 `resume_text` 时 bytes | Task 2 明确 `b""` |
| **—** | **无未关闭项** | **Review status: CLEAN** |
