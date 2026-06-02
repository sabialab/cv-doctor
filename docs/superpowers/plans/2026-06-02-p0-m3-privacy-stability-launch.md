# P0-M3 Privacy, Stability & Launch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Soft-launch P0 on Cloudflare — persistent sessions (D1/R2), 24h auto-delete, parse/LLM degradation, rate limits, upload consent, production deploy.

**Architecture:** `SessionRepository` + **方案 B**（Python 持 D1/R2 业务读写，Worker 代理 + Cron）；见 spec §架构决策。

**Tech Stack:** FastAPI, D1, R2 (S3 API), Wrangler, Hono Worker, Next.js 15, pytest.

**Spec:** [docs/superpowers/specs/2026-06-02-p0-m3-privacy-stability-launch-design.md](../specs/2026-06-02-p0-m3-privacy-stability-launch-design.md)

**Branch:** `feat/p0-m3-launch` from `origin/main`

**Plan revisions:** 2026-06-02 — Review autofix: 方案 B、export R2 下载、resume 二选一、Worker 限流、Task 9 拆分、参数化测试、日志脱敏、staging/真实管线。

---

## Execution order (locked)

```text
Task 4, 4b  (friendly errors, logging)     ∥  Task 1 (repository)
        → Task 2, 3 (resume_text, rate limit)
        → Task 5, 6, 7 (consent, purge, UI)   [7 after 2]
        → Task 8 → Task 8b (spike) → Task 9a → 9b → 9c
        → Task 3b (parametrize tests; add cloudflare backend after 9c)
        → Task 10, 11 (cron, deploy)
        → Task 12, 13 (verify, seed users)
```

---

## File structure (target)

| Path | Responsibility |
|------|----------------|
| `server/src/repositories/session.py` | `SessionRepository` protocol + `get_repository()` |
| `server/src/repositories/memory.py` | In-memory impl |
| `server/src/repositories/r2_store.py` | R2 S3-compatible put/get/delete |
| `server/src/repositories/d1_store.py` | D1 session rows (JSON columns) |
| `server/src/repositories/cloudflare.py` | Composes d1 + r2 → `SessionRepository` |
| `server/src/services/rate_limit.py` | Local FastAPI rate limit |
| `worker/src/rate_limit.ts` | Edge rate limit `POST /api/sessions` |
| `worker/src/cron_purge.ts` | Scheduled TTL cleanup |
| `worker/migrations/0001_sessions.sql` | D1 schema |
| `scripts/purge-expired-sessions.py` | Local TTL |
| `docs/deploy-p0-m3.md` | Staging + production runbook |

---

## M3-A — Stability & degradation

### Task 1: `SessionRepository` protocol + memory migration

**Depends on:** none

**Files:**
- Create: `server/src/repositories/__init__.py`, `session.py`, `memory.py`
- Modify: `server/src/services/session_store.py` → re-export shim (one release) then remove
- Modify: `server/src/main.py`, all `server/tests/*` imports

- [ ] **Step 1: Protocol** — include `resume_text` on create; file helpers `put_resume_bytes`, `put_export_docx`, `open_export_read`, `delete_session_files`.

- [ ] **Step 2: Move `session_store.py` logic → `memory.py`** — preserve `PatchChangeResult`, PolicyGuard-in-lock behavior.

- [ ] **Step 3:** `get_repository()` from `SESSION_BACKEND` (`memory` default).

- [ ] **Step 4:** `pytest -q` green → commit `refactor(server): SessionRepository protocol and memory backend`

---

### Task 4: User-facing pipeline errors

**Depends on:** none（可与 Task 1 并行）

**Files:**
- Modify: `server/src/main.py` (`_run_diagnosis`)
- Create: `server/tests/test_api_failed_session.py`

- [ ] **Step 1:** Test — patch LLM/pipeline to raise → `failed` + Chinese `error` without `Traceback`.

- [ ] **Step 2:** Map `LLMError`, `ValidationError`, generic `Exception` → fixed user messages; `logger.exception` server-side only.

- [ ] **Step 3:** Commit `fix(api): friendly failed-session errors`

---

### Task 4b: Log redaction (§9)

**Depends on:** Task 4

**Files:**
- Modify: `server/src/main.py` or `server/src/logging_config.py`
- Create: `server/tests/test_logging_redaction.py` (optional: caplog)

- [ ] **Step 1:** Ensure no log line includes full `jd_text`, resume body, or `revised` strings (truncate or omit).

- [ ] **Step 2:** Document in `docs/deploy-p0-m3.md` §运维.

- [ ] **Step 3:** Commit `fix(ops): redact resume and JD from request logs`

---

### Task 2: `POST /sessions` resume text fallback

**Depends on:** Task 1

**Files:**
- Modify: `server/src/main.py`, `server/src/pipeline.py` (accept prebuilt `Resume` or `resume_text`)
- Create: `server/tests/test_api_resume_text_fallback.py`

**API contract (locked):**

| Fields | Rule |
|--------|------|
| `resume` | Optional `UploadFile` if `.docx` |
| `resume_text` | Optional `Form` |
| | At least one required |
| `jd_text`, `consent` | Required |

- [ ] **Step 1:** Failing test with `USE_REAL_PIPELINE=1` (or mock parser failure) + `resume_text` only → `ready`.

- [ ] **Step 2:** `_run_diagnosis` passes `resume_text` into pipeline when parser yields empty `Resume`.

- [ ] **Step 3:** Commit `feat(api): resume_text fallback when DOCX parse fails`

---

### Task 3: Rate limit `POST /sessions`

**Depends on:** Task 1

**Files:**
- `server/src/services/rate_limit.py`, `worker/src/rate_limit.ts`
- `server/tests/test_rate_limit.py`, `worker` manual test notes

- [ ] **Step 1:** **Local:** FastAPI middleware/dep — key `request.client.host`; `RATE_LIMIT_SESSIONS_PER_DAY=20`.

- [ ] **Step 2:** **Worker:** Before proxy, count by `CF-Connecting-IP` (fallback `X-Forwarded-For`); return 429 JSON same `detail` string. Ensure `worker/src/index.ts` forwards `CF-Connecting-IP` to Container when needed for logging (rate limit uses edge IP only).

- [ ] **Step 3:** Do **not** enable both on same request path in staging (Worker only in prod; local dev hits FastAPI directly).

- [ ] **Step 4:** Web `apiErrorMessage` for 429.

- [ ] **Step 5:** Commit `feat: rate limit session create at edge and locally`

---

### Task 3b: Parametrized repository contract tests

**Depends on:** Task 1；**`cloudflare` 参数在 Task 9c 完成后追加**

**Files:**
- Modify: `server/tests/test_api.py`, `test_api_patch_change.py` — `@pytest.mark.parametrize("backend", ["memory"])`
- Create: `server/tests/conftest.py` — `backend` fixture swaps `get_repository`

- [ ] **Step 1:** Single test module runs full session flow on `memory`.

- [ ] **Step 2:** After Task 9c, add `"cloudflare"` with moto/HTTP mocks.

- [ ] **Step 3:** Commit `test: parametrize session API by repository backend`

---

## M3-B — Privacy & local TTL

### Task 5: Upload consent

**Depends on:** none（可与 Task 2 并行）

**Files:** `web/app/page.tsx`, `web/lib/api.ts`, `server/src/main.py`, `server/tests/test_api.py`

- [ ] Checkbox + `consent=true`; server 400 without consent.
- [ ] Commit `feat(web): required privacy consent before diagnosis`

---

### Task 6: Local TTL purge script

**Depends on:** Task 1

**Files:** `scripts/purge-expired-sessions.py`, `server/src/repositories/memory.py`, `server/tests/test_purge_expired.py`, `server/.env.example`

- [ ] `list_expired(before)` on memory repo; script + `test_purge_expired.py`.
- [ ] Commit `feat(ops): purge expired local sessions`

---

### Task 7: Frontend parse-fallback UI

**Depends on:** Task 2

- [ ] `createSession` accepts optional `resume` + `resume_text`; show paste UI on parse-related errors.
- [ ] Commit `feat(web): paste resume text fallback`

---

## M3-C — Cloudflare persistence

### Task 8: D1 schema & migrations

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

- [ ] `wrangler.toml` D1 + R2 bindings (commented template + staging/prod names in runbook).
- [ ] Commit `feat(worker): D1 sessions schema`

---

### Task 8b: Container ↔ D1/R2 spike

**Depends on:** Task 8

- [ ] Document in `docs/deploy-p0-m3.md` §Spike: env vars, one read/write proof, or blockers.
- [ ] If spike fails, stop Task 9 until resolved — do not guess APIs.

---

### Task 9a: R2 file store

**Depends on:** Task 8b

- [ ] `r2_store.py`: `uploads/{session_id}/resume.docx`, `exports/{session_id}/resume-export.docx`.
- [ ] Unit tests with mock S3 client.

---

### Task 9b: D1 session metadata

**Depends on:** Task 8b

- [ ] `d1_store.py`: CRUD session row; serialize `DiagnosisResult` → `result_json`.
- [ ] `expires_at` on create from `AUTO_DELETE_HOURS`.

---

### Task 9c: Cloudflare `SessionRepository` + export download

**Depends on:** Task 9a, 9b, Task 1

- [ ] `cloudflare.py` implements full protocol; wire `SESSION_BACKEND=cloudflare`.
- [ ] **Download:** `GET /sessions/{id}/export/download` streams from R2 (replace `FileResponse` when backend=cloudflare).
- [ ] **PATCH change:** clear `export_r2_key` + delete R2 export object (mirror M2 local `export_path` invalidation).
- [ ] Complete Task 3b: add `cloudflare` parametrization with mocks.
- [ ] Commit `feat(server): D1+R2 session repository and R2 export download`

---

## M3-D — Deploy & Cron

### Task 10: Worker Cron purge

- [ ] `cron_purge.ts`: `DELETE FROM sessions WHERE expires_at < ?`; delete R2 keys `uploads/{id}/*`, `exports/{id}/*`.
- [ ] `wrangler.toml` `triggers.crons = ["0 * * * *"]`
- [ ] Commit `feat(worker): hourly cron purge expired sessions`

---

### Task 11: Production deploy runbook

**Files:** `docs/deploy-p0-m3.md`

Must include:

| Section | Content |
|---------|---------|
| Staging | Account/binding names; preview URL |
| Production secrets | `DEEPSEEK_API_KEY`, `USE_REAL_PIPELINE=1` |
| Web | `NEXT_PUBLIC_API_BASE`, Pages build |
| Worker | Forward `CF-Connecting-IP`; rate limit |
| R2 lifecycle | `uploads/`, `exports/` TTL backup |
| §7.3 checklist | Copy from p0-mvp |
| Cold start | Note ≤45s goal may slip; user sees progress steps |

- [ ] Optional CI: `wrangler d1 migrations apply` dry-run.
- [ ] Commit `docs: P0-M3 Cloudflare deploy runbook`

---

## M3-E — Soft launch validation

### Task 12: End-to-end verification

- [ ] Local: `pytest -q`, `npm run build`, stub + **real** pipeline smoke.
- [ ] Staging: §7.3 on staging URL; TTL + 429 + delete session.
- [ ] `cr review --base main --plain`
- [ ] PR squash → checkout `main`, delete `feat/p0-m3-launch`

---

### Task 13: Seed users (product)

- [ ] `docs/seed-user-feedback-template.md` — 完成率、首屏时间、导出、信任 1–5、Go/No-Go 表。

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
| D1/R2 与 memory 不一致 | Task 3b 参数化契约测试 |
| Container 冷启动 | 进度 UI；runbook 写预期 |
| 双重重试/双限流 | Worker 限流仅生产路径；本地仅 FastAPI |
| Cron 误删 | `expires_at` + staging 演练 |
| Spike 失败 | Task 8b 闸门，不强行合并 9 |

---

## Doc updates

- [x] `docs/p0-mvp-implementation.md` — Phase 3 链接（`docs/p0-m3-plan`）
- [x] `docs/architecture.md` — M3 当前计划
- [ ] `README.md` — 生产 URL（Task 11 后填写）

---

## Summary

| 里程碑 | 交付 |
|--------|------|
| M3-A | 降级 + 限流 + 友好错误 + 日志脱敏 |
| M3-B | 同意勾选 + 本地 TTL + 粘贴 UI |
| M3-C | D1 + R2 + R2 导出下载 |
| M3-D | Cron + runbook + 真实管线生产配置 |
| M3-E | Staging 验收 + 种子用户 |

---

## Review log (2026-06-02)

| Round | 发现 | 处理 |
|-------|------|------|
| 1 | D1/R2 方案未定 | 锁定方案 B + Task 8b spike |
| 1 | 导出下载未规划 R2 | Task 9c 流式下载 + PATCH 失效 |
| 1 | resume 必填 .docx 与降级矛盾 | API：resume 与 resume_text 二选一 |
| 1 | 双限流 | Worker（生产）vs FastAPI（本地） |
| 1 | 生产 stub | runbook 强制 `USE_REAL_PIPELINE=1` |
| 2 | Task 3b 顺序 | 移到 9c 之后 |
| 2 | IP 头名称 | `X-Forwarded-For`；限流仅在边缘 |
| 3 | R2 路径不一致 | 统一 `resume-export.docx` |
| 3 | Task 5/6 缺 Files | 已补 |
