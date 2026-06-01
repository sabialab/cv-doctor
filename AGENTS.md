# AGENTS.md — CV-Doctor

Open, tool-agnostic instructions for AI coding agents (Cursor, Claude Code, Codex, Copilot, etc.).

**Canonical detail:** [`CLAUDE.md`](CLAUDE.md) is the full reference. This file summarizes execution standards and points to scoped rules.

Behavioral baseline: [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) (Think → Simplicity → Surgical → Goal-Driven).

---

## Project

| Field | Value |
|-------|--------|
| Name | CV-Doctor / 简历对症下药 |
| Goal | Paste JD → auditable resume surgery → export DOCX |
| Current phase | **P0 Web MVP** — see `docs/p0-mvp-implementation.md` |
| UI language | Simplified Chinese |
| Anti-goal | Generic AI rewrite; fabricated experience; ATS keyword stuffing |

---

## Quick rules for agents

1. **Read** `docs/p0-mvp-implementation.md` before implementing product features.
2. **Extend** `server/src/models.py` — do not invent parallel domain types.
3. **Never** auto-apply high-risk resume changes; enforce `PolicyGuard`.
4. **LLM** outputs must be schema-validated JSON (Pydantic).
5. **Minimal diff** — P0 only; no P1 scrape/profile unless user explicitly expands scope.
6. **Verify** — `pytest` / `npm run build` before claiming completion.

---

## Repository map

| Path | Role |
|------|------|
| `server/` | FastAPI backend, parsers, LLM pipeline |
| `web/` | Next.js frontend |
| `cli/` | Debug CLI (not user-facing in P0) |
| `skills/` | Portable Cursor skills (e.g. Karpathy guidelines) |
| `PLAN.md` | Long-term roadmap |
| `docs/architecture.md` | System architecture (P0-aligned) |
| `docs/p0-mvp-implementation.md` | **Active sprint spec** |

---

## Cursor

Committed rules live in `.cursor/rules/`:

| Rule | Scope |
|------|--------|
| `karpathy-guidelines.mdc` | Always — behavioral baseline |
| `cv-doctor-core.mdc` | Always — project + P0 + docs hierarchy |
| `llm-trust-boundary.mdc` | Always — anti-hallucination |
| `server-python.mdc` | `server/**` |
| `web-frontend.mdc` | `web/**` |

See [`CURSOR.md`](CURSOR.md) for setup.

### Global skill (optional)

Install repo skill for all Cursor projects:

```bash
mkdir -p ~/.cursor/skills
cp -R skills/karpathy-guidelines ~/.cursor/skills/karpathy-guidelines
```

Source: [`skills/karpathy-guidelines/SKILL.md`](skills/karpathy-guidelines/SKILL.md) (mirrors [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)).

---

## Claude Code

Use root [`CLAUDE.md`](CLAUDE.md) as project instructions.

---

## Contributing

See [`docs/contributing.md`](docs/contributing.md). Commits: `feat:`, `fix:`, `docs:`, `test:`.

When changing Karpathy-style principles, sync `CLAUDE.md`, `AGENTS.md`, and `.cursor/rules/karpathy-guidelines.mdc`.
