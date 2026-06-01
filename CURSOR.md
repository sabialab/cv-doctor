# Using agent rules in Cursor — CV-Doctor

This repo ships **Cursor project rules** so Karpathy-style behavioral guidelines and CV-Doctor domain constraints apply automatically.

## In this repository

1. Open the folder in Cursor.
2. Rules under [`.cursor/rules/`](.cursor/rules/) are committed. Key files:
   - `karpathy-guidelines.mdc` — `alwaysApply: true` (behavioral baseline)
   - `cv-doctor-core.mdc` — `alwaysApply: true` (project + P0 scope)
   - `llm-trust-boundary.mdc` — `alwaysApply: true` (anti-hallucination)
   - `server-python.mdc` — when editing `server/**`
   - `web-frontend.mdc` — when editing `web/**`
3. Confirm under **Cursor Settings → Rules** (or Project Rules UI) that these appear.

## Other tools in the same repo

| Tool | File to read |
|------|----------------|
| Claude Code | [`CLAUDE.md`](CLAUDE.md) |
| Any agent | [`AGENTS.md`](AGENTS.md) |

Cursor does **not** load `.claude-plugin/` or `CLAUDE.md` by default.

## Global user skill (`~/.cursor/skills`)

This repo also ships a **Skill** (not only project rules). Install once for every workspace:

```bash
mkdir -p ~/.cursor/skills
cp -R skills/karpathy-guidelines ~/.cursor/skills/karpathy-guidelines
```

After copying, new Agent chats can pick up `karpathy-guidelines` from the skill description, or you can @-mention it.

Project-specific rules (CV-Doctor anti-hallucination, P0 scope) remain in `.cursor/rules/` — do not rely on the global skill alone when working in this repo.

## Reuse in another project

**Cursor (project rules):** Copy selected `.mdc` files into that project's `.cursor/rules/`.

**Karpathy baseline (global skill):** Copy `skills/karpathy-guidelines/` to `~/.cursor/skills/karpathy-guidelines/`, or use upstream [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills).

**Karpathy baseline (rules file):** Copy [andrej-karpathy-skills `.cursor/rules/karpathy-guidelines.mdc`](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/.cursor/rules/karpathy-guidelines.mdc) or merge [`CLAUDE.md`](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md) into your root instructions.

## Upstream reference

Behavioral principles trace to [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills). When updating principles, keep `CLAUDE.md`, `AGENTS.md`, and `karpathy-guidelines.mdc` in sync.

## For contributors

- Product behavior changes → update `docs/p0-mvp-implementation.md` and `cv-doctor-core.mdc`.
- Trust/safety policy changes → update `llm-trust-boundary.mdc` and `server/src/models.py` (`PolicyGuard`).
