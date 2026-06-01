# CLAUDE.md — CV-Doctor

Instructions for AI coding agents working in this repository. Behavioral baseline adapted from [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills); project rules below are CV-Doctor–specific.

**Tradeoff:** Guidelines bias toward caution and verifiability over speed. For trivial chores, use judgment.

---

## Part A — Behavioral guidelines (Karpathy)

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — do not pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what is confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that was not requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask: "Would a senior engineer call this overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Do not "improve" adjacent code, comments, or formatting.
- Do not refactor unrelated broken-looking code unless asked.
- Match existing style, even if you would do it differently.
- If you notice unrelated dead code, mention it — do not delete it.

When your changes create orphans:

- Remove imports/variables/functions that **your** changes made unused.
- Do not remove pre-existing dead code unless asked.

Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Tests pass before and after"

For multi-step tasks, state a brief plan with verify steps per step.

Strong success criteria allow independent verification. Weak criteria ("make it work") require constant clarification.

---

## Part B — Project context

### What this repo is

**CV-Doctor（简历对症下药）** — AI resume surgery for Chinese job seekers.

- **Not** a resume generator, generic polish tool, or ATS score gimmick.
- **Is** auditable diffs (原文/改文/依据/风险), anti-hallucination, JD gap diagnosis, mobile-first Web.

**One-liner:** Paste a job description → get a reviewable surgery list → accept/reject → export DOCX.

**Product copy and UX strings:** Simplified Chinese (`zh-CN`). Code comments and agent docs: English or bilingual as team prefers.

### Sources of truth (read before large changes)

| Priority | Document | Use for |
|----------|----------|---------|
| 1 | `PLAN.md` | Vision, phases P0–P3, positioning, what we are / are not |
| 2 | `docs/p0-mvp-implementation.md` | **Current build target** — APIs, milestones, acceptance, file layout |
| 3 | `docs/mvp-feasibility.md` | Scope feasibility, risks |
| 4 | `server/src/models.py` | Domain types: `Fact`, `EvidenceStore`, `Change`, `PolicyGuard`, `MatchScore`, etc. |
| 5 | `README.md` | Quick start, user-facing feature list |

If `PLAN.md` and `docs/p0-mvp-implementation.md` disagree on P0 scope, **P0 implementation doc wins** for what to build now.

### Repository layout

```text
cv-doctor/
├── server/          # FastAPI + LiteLLM + python-docx (Python 3.11+)
├── web/             # Next.js 15 + React 19 + Tailwind 4
├── cli/             # Typer CLI — internal/debug only in P0
├── docs/            # Architecture, contributing, P0 plan
├── PLAN.md
├── CLAUDE.md        # This file (Claude Code)
├── AGENTS.md        # Cross-tool agent instructions
└── CURSOR.md        # Cursor-specific setup
```

### Tech stack (do not swap without discussion)

| Layer | Choice |
|-------|--------|
| API | FastAPI, Pydantic v2, `uvicorn` |
| LLM | LiteLLM → DeepSeek V4 Flash (config via env) |
| Resume I/O | `python-docx`; PDF best-effort in P0 |
| Web | Next.js App Router, TypeScript strict |
| Lint/test (server) | Ruff, pytest, mypy-friendly types |

### P0 scope guardrails

**In scope now:** Web upload DOCX → paste JD → diagnose → show ≤3 free `Change` diffs → accept/reject/edit → export DOCX only accepted changes; session storage; privacy copy (24h delete).

**Out of scope now (do not implement unless explicitly asked):** BOSS/拉勾 scrape, 天眼查, company profiling, multi-JD, paid wall, user accounts, CLI as main UX, Kimi K2.6 reports, PDF export polish, SEO landing pages (optional post-M3).

When asked to "build the product", default to **P0 implementation doc**, not full `PLAN.md` P1/P2 features.

---

## Part C — Domain rules (non-negotiable)

### LLM trust boundary

This product's reputation depends on **never inventing resume facts**.

- Every `Change` must cite `evidence_ids` from `EvidenceStore` / resume facts when present in schema.
- Implement and respect `PolicyGuard` rules in `models.py`: `FORBIDDEN` / `NEEDS_CONFIRMATION` / `ALLOWED`.
- **High-risk changes must not be auto-applied** on export — user must explicitly accept.
- LLM outputs: **JSON only**, validated with Pydantic; retry on schema failure; no silent truncation of safety fields.
- Do not add "helpful" fictional metrics, employers, or skills to please the user.

### Result UX order (P0)

On the diagnosis result screen, information order is fixed:

1. JD plain-language summary (这个岗位在招什么人)
2. Matched requirements
3. Partially matched
4. Missing (补充建议 only — not written into resume as fact)
5. Up to 3 free surgery suggestions (diff cards with risk)
6. Match Score is **secondary**, not the hero metric

### Privacy

- No logging of raw resume/JD to third-party analytics without explicit design review.
- Session files: treat as sensitive; align with 24h TTL and delete APIs in P0 plan.
- Do not commit secrets; use `.env` / `.env.example` only.

---

## Part D — Development conventions

### Server (`server/`)

- All API request/response bodies: Pydantic models (extend `models.py` or `schemas/` as doc'd in P0 plan).
- New pipeline steps: pure functions or small services under `server/src/services/`, orchestrated from `main.py`.
- LLM calls: single module (e.g. `llm_client.py`), structured outputs, timeouts, bounded retries.
- Tests required for: parsers, policy guard, export merge logic, API happy paths.

### Web (`web/`)

- Mobile-first layouts; touch targets ≥44px; avoid desktop-only flows for P0.
- API types should mirror server Pydantic shapes; share OpenAPI or hand-written types consistently.
- User-visible strings in Chinese; keep tone direct and honest (no overpromising AI).

### Git / commits

Follow `docs/contributing.md`: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).

### Verification before claiming done

- Server: `pytest` passes; `ruff check` clean for touched files.
- Web: `npm run build` succeeds; manual smoke on upload → result → export if UI changed.
- Any LLM behavior change: describe how hallucination/risk cases were considered.

---

## Part E — Sync with other agent files

When editing behavioral principles, keep these aligned:

- `CLAUDE.md` (this file)
- `AGENTS.md`
- `.cursor/rules/karpathy-guidelines.mdc`
- `.cursor/rules/cv-doctor-core.mdc` (project-specific)

Upstream reference: [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills).
