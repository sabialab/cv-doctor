# P0-M3 Privacy, Stability & Launch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Soft-launch P0 on Cloudflare — persistent sessions (D1/R2), 24h auto-delete, parse/LLM degradation, rate limits, upload consent, production deploy.

**Architecture:** Extract `SessionRepository`; add optional `resume_text` on create; local purge script then Worker Cron; deploy Pages + Worker + Container per [p0-cloudflare-stack.md](../../p0-cloudflare-stack.md).

**Tech Stack:** FastAPI, D1 (SQL), R2, Wrangler, Hono Worker, Next.js 15, pytest.

**Spec:** [docs/superpowers/specs/2026-06-02-p0-m3-privacy-stability-launch-design.md](../specs/2026-06-02-p0-m3-privacy-stability-launch-design.md)

**Branch:** `feat/p0-m3-launch` from `origin/main`

**Work packages:** M3-A (stability) → M3-B (privacy/TTL local) → M3-C (D1/R2) → M3-D (deploy/cron) → M3-E (seed users)

---

## File structure (target)

| Path | Responsibility |
|------|----------------|
| `server/src/repositories/session.py` | `SessionRepository` protocol |
| `server/src/repositories/memory.py` | In-memory impl (from `session_store`) |
| `server/src/repositories/d1_r2.py` | Cloudflare D1 + R2 impl |
| `server/src/services/rate_limit.py` | IP daily limit for `POST /sessions` |
| `server/src/main.py` | Wire repo, `resume_text`, consent, 429 |
| `worker/src/index.ts` | Existing proxy + Cron handler |
| `worker/migrations/0001_sessions.sql` | D1 schema |
| `worker/wrangler.toml` | D1/R2 bindings, cron, secrets |
| `scripts/purge-expired-sessions.py` | Local/staging TTL purge |
| `web/app/page.tsx` | Consent checkbox + resume paste fallback UI |
| `web/lib/api.ts` | `createSession` optional `resume_text`, 429 handling |
| `docs/deploy-p0-m3.md` | One-page deploy runbook (optional) |

---

## M3-A — Stability & degradation

### Task 1: `SessionRepository` protocol + memory migration

**Files:**
- Create: `server/src/repositories/__init__.py`, `session.py`, `memory.py`
- Modify: `server/src/services/session_store.py` → thin re-export or delete after migration
- Modify: `server/src/main.py`, `server/tests/*`

- [ ] **Step 1: Define protocol**

```python
# server/src/repositories/session.py
class SessionRepository(Protocol):
    def create_session(self, *, resume_bytes: bytes, jd_text: str, resume_text: str | None = None) -> SessionRecord: ...
    def get_session(self, session_id: str) -> SessionRecord | None: ...
    def update_session(self, session_id: str, **kwargs: object) -> SessionRecord | None: ...
    def patch_change(...) -> PatchChangeResult: ...
    def delete_session(self, session_id: str) -> bool: ...
```

- [ ] **Step 2: Move logic from `session_store.py` to `memory.py`** — behavior unchanged; tests green.

- [ ] **Step 3: `main.py` uses `get_repository()` from env `SESSION_BACKEND=memory` (default).**

- [ ] **Step 4: Commit**

```bash
git commit -m "refactor(server): SessionRepository protocol and memory backend"
```

---

### Task 2: `POST /sessions` resume text fallback

**Files:**
- Modify: `server/src/main.py`, `server/src/api/schemas.py`
- Create: `server/tests/test_api_resume_text_fallback.py`

- [ ] **Step 1: Failing test** — POST with empty/invalid docx + `resume_text` → `ready` and result uses text path.

- [ ] **Step 2: Accept `resume_text: str | None = Form(None)`** on create; if parser yields empty/minimal resume, build `Resume(raw_text=resume_text)` and continue pipeline/stub.

- [ ] **Step 3: `pytest` + commit**

```bash
git commit -m "feat(api): resume_text fallback when DOCX parse fails"
```

---

### Task 3: Rate limit `POST /sessions`

**Files:**
- Create: `server/src/services/rate_limit.py`, `server/tests/test_rate_limit.py`
- Modify: `server/src/main.py`, `server/src/config.py`

- [ ] **Step 1: Test** — same IP > N creates → 429.

- [ ] **Step 2: Implement in-memory sliding window or daily counter keyed by `X-Forwarded-For` / client host; `RATE_LIMIT_SESSIONS_PER_DAY=20`.**

- [ ] **Step 3: Map 429 body `{ "detail": "今日诊断次数已达上限，请明日再试" }`.**

- [ ] **Step 4: Web `createSession` surfaces 429 via `apiErrorMessage`.**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(api): daily rate limit on session create"
```

---

### Task 4: User-facing pipeline errors

**Files:**
- Modify: `server/src/main.py` (`_run_diagnosis`), `server/src/llm/client.py`
- Create: `server/tests/test_api_failed_session.py`

- [ ] **Step 1: Test** — mock LLM raise → GET session `failed` + Chinese `error` without stack trace.

- [ ] **Step 2: Catch `LLMError`, `ValidationError` → friendly messages; log exception server-side only.**

- [ ] **Step 3: Optional: increase `max_retries` to 2 for production via config.**

- [ ] **Step 4: Commit**

```bash
git commit -m "fix(api): friendly failed-session errors for LLM/pipeline"
```

---

## M3-B — Privacy & local TTL

### Task 5: Upload consent (frontend + API)

**Files:**
- Modify: `web/app/page.tsx`, `web/lib/api.ts`
- Modify: `server/src/main.py` (optional `consent: bool = Form(...)`)

- [ ] **Step 1: Checkbox** — required before submit; label links `/privacy`.

- [ ] **Step 2: Form field `consent=true`**; server returns 400 if missing (test in `test_api.py`).

- [ ] **Step 3: `npm run build` + commit**

```bash
git commit -m "feat(web): required privacy consent before diagnosis"
```

---

### Task 6: Local TTL purge script

**Files:**
- Create: `scripts/purge-expired-sessions.py`
- Modify: `server/src/repositories/memory.py` — expose `list_expired(before: datetime)`
- Create: `server/tests/test_purge_expired.py`

- [ ] **Step 1: Test** — create session with old `created_at` → purge removes it + export file.

- [ ] **Step 2: Script reads `AUTO_DELETE_HOURS` (default 24), deletes expired from memory repo + `EXPORT_DIR`.**

- [ ] **Step 3: Document in README / `server/.env.example`.**

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(ops): purge expired local sessions by AUTO_DELETE_HOURS"
```

---

### Task 7: Frontend parse-fallback UI

**Files:**
- Modify: `web/app/page.tsx`, `web/lib/api.ts`

- [ ] **Step 1: On create error containing「解析」/「DOCX」**, show collapsible「粘贴简历全文」textarea; resubmit with same JD + `resume_text`.

- [ ] **Step 2: Manual smoke on stub + corrupt docx fixture.**

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(web): paste resume text fallback on parse failure"
```

---

## M3-C — Cloudflare persistence

### Task 8: D1 schema & migrations

**Files:**
- Create: `worker/migrations/0001_sessions.sql`
- Modify: `worker/wrangler.toml`

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
  export_r2_key TEXT
);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
```

- [ ] **Step 1: Add D1 binding `DB` in wrangler.toml.**

- [ ] **Step 2: CI step: `wrangler d1 migrations apply DB --local` (or document manual).**

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(worker): D1 sessions schema migration"
```

---

### Task 9: R2 + D1 `SessionRepository`

**Files:**
- Create: `server/src/repositories/d1_r2.py` (or split `d1.py` + `r2_files.py`)
- Create: `server/tests/test_repository_d1_r2.py` (use wrangler local / moto-style mocks)

- [ ] **Step 1: Implement create/get/update/delete/patch_change** mirroring memory semantics.

- [ ] **Step 2: Store `resume_bytes` at `uploads/{id}/resume.docx`; export at `exports/{id}/resume-export.docx`.**

- [ ] **Step 3: Set `expires_at = created_at + AUTO_DELETE_HOURS` on create.**

- [ ] **Step 4: `SESSION_BACKEND=cloudflare` + env bindings for dev container.**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(server): D1+R2 session repository for production"
```

---

## M3-D — Deploy & Cron

### Task 10: Worker Cron purge

**Files:**
- Modify: `worker/src/index.ts`
- Modify: `worker/wrangler.toml` — `triggers.crons = ["0 * * * *"]`

- [ ] **Step 1: Scheduled handler** — query D1 `expires_at < now()`, delete rows + R2 objects by prefix.

- [ ] **Step 2: Integration test or manual wrangler dev + curl scheduled.**

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(worker): hourly cron purge expired sessions"
```

---

### Task 11: Production deploy runbook

**Files:**
- Create: `docs/deploy-p0-m3.md` (or extend `p0-cloudflare-stack.md` §6 checklist)
- Modify: `.github/workflows/ci.yml` (optional container build job)

- [ ] **Step 1: Document** Pages build, Worker deploy, Container secret `DEEPSEEK_API_KEY`, `ALLOWED_ORIGINS`, `NEXT_PUBLIC_API_BASE`.

- [ ] **Step 2: Staging URL smoke checklist (copy §7.3).**

- [ ] **Step 3: R2 lifecycle rule doc for `uploads/` + `exports/`.**

- [ ] **Step 4: Commit**

```bash
git commit -m "docs: P0-M3 Cloudflare deploy runbook"
```

---

## M3-E — Soft launch validation

### Task 12: End-to-end verification

- [ ] **Step 1: Local** — `pytest -q`, `npm run build`, stub + real pipeline smoke.

- [ ] **Step 2: Staging** — full §7.3 checklist on production-like env.

- [ ] **Step 3: `cr review --base main --plain`**

- [ ] **Step 4: PR squash merge** — post-merge: `git checkout main && git pull && git branch -d feat/p0-m3-launch`

---

### Task 13: Seed users (product)

**Files:**
- Create: `docs/seed-user-feedback-template.md` (optional)

| # | 动作 |
|---|------|
| 1 | 招募 5–10 人（同事/朋友），真实 JD + 简历 |
| 2 | 记录：完成率、首屏时间、是否导出、主观信任 1–5 |
| 3 | 汇总 Go/No-Go 对照 §1.3 表格 |

- [ ] **Not a code commit** — track in Issue or spreadsheet.

---

## Verification commands (each PR slice)

```bash
cd server && uv sync --extra dev --frozen && uv run ruff check src/ tests/ && uv run pytest -q
cd web && npm ci && npm run build
cd worker && npm ci && npx wrangler deploy --dry-run  # when configured
```

---

## Risk register

| 风险 | 对策 |
|------|------|
| D1/R2 与本地内存行为不一致 | 共享 pytest 契约测试套件；同一 `test_api.py` 对两种 backend 参数化 |
| Container 冷启动慢 | 异步诊断已在架构预留；M3 仍轮询，文档写首屏 ≤45s 目标 |
| Cron 误删 | 仅删 `expires_at` 已过；staging 先测 |
| 限流误伤 NAT | P0 用宽松阈值；日志记录 IP hash |

---

## Doc updates (final PR)

- [ ] `docs/p0-mvp-implementation.md` — Phase 3 链接到本 plan
- [ ] `docs/architecture.md` —「当前」计划改为 M3；M2 标为已完成
- [ ] `README.md` — 生产 URL（合并后填写）

---

## Summary

| 里程碑 | 交付 |
|--------|------|
| M3-A | 降级 + 限流 + 友好错误 |
| M3-B | 勾选同意 + 本地 TTL + 粘贴 UI |
| M3-C | D1 + R2 持久化 |
| M3-D | Cron + 公网部署 |
| M3-E | 种子用户与指标 |

**M2 已证明产品闭环；M3 证明可上线、可合规、可运维。**
