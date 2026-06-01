# Using agent rules in Cursor — CV-Doctor

This repo ships **Cursor project rules** plus optional **global skills** so behavioral and domain constraints apply automatically.

## Authority order

0. **Superpowers plugin (Cursor)** — invoke matching skills **before any other action**; see [CLAUDE.md §0](CLAUDE.md#0-superpowers-插件--会话级最高优先级) and `.cursor/rules/superpowers.mdc`
1. **[`CLAUDE.md`](CLAUDE.md)** — highest standard (Chinese-first; full verify & PR rules)
2. **[`AGENTS.md`](AGENTS.md)** — cross-tool summary; defers to `CLAUDE.md` on conflict
3. **`.cursor/rules/*.mdc`** — scoped automation in the IDE

## In this repository

1. Open the folder in Cursor.
2. Committed rules under [`.cursor/rules/`](.cursor/rules/):

| File | When it applies |
|------|----------------|
| `superpowers.mdc` | Always — **Superpowers plugin first** (skills routing) |
| `karpathy-guidelines.mdc` | Always — Think / Simplicity / Surgical / Verify |
| `cv-doctor-core.mdc` | Always — product, P0 scope, doc hierarchy |
| `llm-trust-boundary.mdc` | Always — anti-hallucination, PolicyGuard |
| `server-python.mdc` | Files under `server/**` |
| `web-frontend.mdc` | Files under `web/**` |

3. Confirm under **Cursor Settings → Rules** (or Project Rules UI) that these appear.

## Other tools in the same repo

| Tool | File to read |
|------|----------------|
| Claude Code | [`CLAUDE.md`](CLAUDE.md) |
| Codex / Copilot / others | [`AGENTS.md`](AGENTS.md) |

Cursor does **not** load `CLAUDE.md` automatically — use project rules + `@` skills.

## Global user skill (`~/.cursor/skills`)

Optional install for Karpathy baseline in every workspace:

```bash
mkdir -p ~/.cursor/skills
cp -R skills/karpathy-guidelines ~/.cursor/skills/karpathy-guidelines
```

CV-Doctor-specific rules (P0 scope, trust boundary) stay in `.cursor/rules/` — do not rely on the global skill alone in this repo.

## PR workflow (agents)

When creating or updating a PR, follow [`CLAUDE.md` §5](CLAUDE.md#5-pr-与-review-规则): trigger `@copilot review` and `@codex review`, run `cr review --base main --plain` when available, and ensure GitHub Actions (`server` / `web` / `worker`) pass. Worker job requires **Node 22+**.

## For contributors

| Change type | Update |
|------------|--------|
| Product / P0 scope | `docs/p0-mvp-implementation.md`, `cv-doctor-core.mdc` |
| Deploy / CF | `docs/p0-cloudflare-stack.md`, `CLAUDE.md` §2–3 |
| Trust / PolicyGuard | `llm-trust-boundary.mdc`, `server/src/models.py` |
| Karpathy principles | `CLAUDE.md` §1, `AGENTS.md`, `karpathy-guidelines.mdc`, `skills/karpathy-guidelines/` |
| Superpowers routing | `CLAUDE.md` §0, `superpowers.mdc`, `AGENTS.md` rule 0 |

## Upstream reference

[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — keep principle files in sync when updating §1.
