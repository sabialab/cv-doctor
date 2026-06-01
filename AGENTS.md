# AGENTS.md — CV-Doctor

Open, tool-agnostic instructions for AI coding agents (Cursor, Claude Code, Codex, Copilot, etc.).

**Canonical source:** [`CLAUDE.md`](CLAUDE.md) is the full execution standard. **If this file conflicts with `CLAUDE.md`, follow `CLAUDE.md`.**

Behavioral baseline: [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — Think → Simplicity → Surgical → Goal-Driven.

**Priority order:** [CLAUDE.md §1 Karpathy](CLAUDE.md#1-通用行为准则andrej-karpathy-风格--第一优先级) (**first**) → [§0 Superpowers](CLAUDE.md#0-superpowers-插件--会话级最高优先级) → product/trust → [§5–7 PR workflow](CLAUDE.md#6-github-pr-工作流).

**Workflow baseline:** Superpowers skills when installed — see `.cursor/rules/superpowers.mdc`. PR: squash merge only, CodeRabbit P1/P2=0 before push, `@copilot`/`@codex` review after push — see `.cursor/rules/pr-workflow.mdc`.

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

0. **Branch from `origin/main` per MVP phase** — After a PR merges, never continue the next phase on that branch. New work: `git checkout -b feat/<phase>-<topic> origin/main`. See [CLAUDE.md §6](CLAUDE.md#6-git-分支与-mvp-阶段工作流强制).
1. **Superpowers first (Cursor):** At session start read `using-superpowers`; before creative work → `brainstorming`; before implement → `test-driven-development` / `executing-plans`; before claiming done → `verification-before-completion`. Full routing: [CLAUDE.md §0](CLAUDE.md#0-superpowers-插件--会话级最高优先级), `.cursor/rules/superpowers.mdc`.
2. **Read** `docs/p0-mvp-implementation.md` and `docs/p0-cloudflare-stack.md` before large product or deploy changes.
3. **Respect** `server/src/models.py` (`PolicyGuard`) and **extend** `server/src/p0_models.py` for P0 API shapes — do not fork parallel domain types.
4. **Never** auto-apply high-risk resume edits; session status uses `ready` / `failed`, not `done`, unless you update API + web + tests together.
5. **Pipeline:** default `USE_REAL_PIPELINE=0` (stub, CI); set `USE_REAL_PIPELINE=1` + `DEEPSEEK_API_KEY` for real parse/LLM/DOCX export.
6. **Minimal diff** — no P1 scrape/profile unless the user explicitly expands scope.
7. **Verify** — see [CLAUDE.md §4](CLAUDE.md#4-验证清单); CI mirrors server / web / worker jobs.
8. **PR** — `cr review --base main --plain` before push (P1/P2=0); squash merge to `main`; sync README/CHANGELOG/versions on merge — [CLAUDE.md §6–7](CLAUDE.md#6-github-pr-工作流).

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
| `karpathy-guidelines.mdc` | Always — **first priority** behavioral baseline |
| `pr-workflow.mdc` | Always — GitHub PR, squash merge, CI, CodeRabbit, release sync |
| `superpowers.mdc` | Always — Superpowers skill routing |
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

When changing Karpathy principles, PR workflow, Superpowers routing, or P0 boundaries, sync `CLAUDE.md`, `AGENTS.md`, `docs/contributing.md`, and `.cursor/rules/{karpathy-guidelines,pr-workflow,superpowers,cv-doctor-core}.mdc`.
