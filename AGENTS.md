# AGENTS.md — CV-Doctor

Open, tool-agnostic instructions for AI coding agents (Cursor, Claude Code, Codex, Copilot, etc.).

**Canonical source:** [`CLAUDE.md`](CLAUDE.md) is the full execution standard. **If this file conflicts with `CLAUDE.md`, follow `CLAUDE.md`.**

Behavioral baseline: [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — Think → Simplicity → Surgical → Goal-Driven.

---

## Project

| Field | Value |
|-------|--------|
| Name | CV-Doctor / 简历对症下药 |
| Goal | Paste JD → auditable resume surgery → export accepted changes |
| Active branch context | P0 MVP on **Cloudflare** (Worker + Pages target); local dev often **Python + Next only** |
| UI language | Simplified Chinese (`zh-CN`) |
| Anti-goals | Generic AI rewrite; fabricated experience; keyword stuffing without evidence |

---

## Quick rules for agents

1. **Read** `docs/p0-mvp-implementation.md` and `docs/p0-cloudflare-stack.md` before large product or deploy changes.
2. **Respect** `server/src/models.py` (`PolicyGuard`) and **extend** `server/src/p0_models.py` for P0 API shapes — do not fork parallel domain types.
3. **Never** auto-apply high-risk resume edits; session status uses `ready` / `failed`, not `done`, unless you update API + web + tests together.
4. **Know the stub:** current diagnosis path is `stub_pipeline` + in-memory `SessionStore` — not full DOCX/LLM until wired.
5. **Minimal diff** — no P1 scrape/profile unless the user explicitly expands scope.
6. **Verify** — see [CLAUDE.md §4](CLAUDE.md#4-验证清单); CI mirrors server / web / worker jobs.

---

## Repository map

| Path | Role |
|------|------|
| `server/` | FastAPI (`main.py`), P0 routes, `session_store`, `stub_pipeline` |
| `web/` | Next.js frontend (`/`, `/s/[id]`, `/privacy`) |
| `worker/` | Cloudflare Worker API proxy (Hono + wrangler) |
| `cli/` | Debug CLI (not user-facing in P0) |
| `docs/p0-cloudflare-stack.md` | **Deploy target** (R2/D1/Container/Cron) |
| `docs/p0-mvp-implementation.md` | **Product acceptance** |
| `PLAN.md` | Long-term roadmap (P1+) |
| `.github/workflows/ci.yml` | CI: Ruff (P0 paths only), pytest, web build, worker tsc + wrangler dry-run |

---

## Cursor

Committed rules: [`.cursor/rules/`](.cursor/rules/)

| Rule | Scope |
|------|--------|
| `karpathy-guidelines.mdc` | Always — behavioral baseline |
| `cv-doctor-core.mdc` | Always — product + docs hierarchy + P0 guardrails |
| `llm-trust-boundary.mdc` | Always — anti-hallucination |
| `server-python.mdc` | `server/**` |
| `web-frontend.mdc` | `web/**` |

Setup: [`CURSOR.md`](CURSOR.md)

Optional global skill:

```bash
mkdir -p ~/.cursor/skills
cp -R skills/karpathy-guidelines ~/.cursor/skills/karpathy-guidelines
```

---

## Claude Code

Use root [`CLAUDE.md`](CLAUDE.md) as project instructions (Chinese-first authority doc).

---

## Contributing

[`docs/contributing.md`](docs/contributing.md) — Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).

When changing Karpathy principles or P0 boundaries, sync `CLAUDE.md`, `AGENTS.md`, and `.cursor/rules/karpathy-guidelines.mdc` + `cv-doctor-core.mdc`.
