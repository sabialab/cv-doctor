# Using agent rules in Cursor — CV-Doctor

This repo ships **Cursor project rules** plus optional **global skills** so behavioral and domain constraints apply automatically.

## Authority order

1. **[`CLAUDE.md`](CLAUDE.md) §1** — **Karpathy 通用行为准则（第一优先级）**
2. **Superpowers plugin** — skill routing; [§0](CLAUDE.md#0-superpowers-插件--会话级最高优先级) + `superpowers.mdc`
3. **PR workflow** — `pr-workflow.mdc` + [CLAUDE.md §5–7](CLAUDE.md#6-github-pr-工作流)
4. **[`AGENTS.md`](AGENTS.md)** — cross-tool summary
5. **`.cursor/rules/*.mdc`** — scoped automation

## Superpowers — install and mandatory use

**Agents MUST use Superpowers** for feature work, plans, and “done” claims. Routing: `.cursor/rules/superpowers.mdc`, [CLAUDE.md §0](CLAUDE.md#0-superpowers-插件--会话级最高优先级).

### Install (if not already active)

1. **Cursor Agent** (`Cmd+L` / `Ctrl+L`) — run:

```text
/plugin-add superpowers
```

2. **Verify** (new Agent session):

```text
Do you have superpowers? List available skills.
```

3. **Fallback** — sync skill files for `@brainstorming` / `@writing-plans` when the plugin Skill tool is unavailable:

```bash
./scripts/install-superpowers-skills.sh
```

Details: [docs/superpowers/README.md](docs/superpowers/README.md).

### Mandatory skill flow (features & plans)

| Step | Skill | Output location |
|------|--------|-----------------|
| Before design / UX / API shape | `brainstorming` | `docs/superpowers/specs/YYYY-MM-DD-<feature>-design.md` |
| Before multi-step implementation | `writing-plans` | `docs/superpowers/plans/YYYY-MM-DD-<feature>.md` |
| During implementation | `test-driven-development` | code + tests |
| Before “done” / merge | `verification-before-completion` | command output in reply |

**Forbidden:** writing a large implementation plan in `docs/p0-*.md` only, without `writing-plans` format (header, checkbox tasks, TDD steps). Legacy docs may link to a Superpowers plan.

**Announce** when invoking a skill: e.g. “Using the writing-plans skill to create the implementation plan.”

## In this repository

1. Open the folder in Cursor.
2. Committed rules under [`.cursor/rules/`](.cursor/rules/):

| File | When it applies |
|------|----------------|
| `karpathy-guidelines.mdc` | Always — **first priority** (Think / Simplicity / Surgical / Verify) |
| `pr-workflow.mdc` | Always — PR, squash merge, CodeRabbit, CI, release sync |
| `superpowers.mdc` | Always — Superpowers skills routing |
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
| Karpathy / PR workflow | `CLAUDE.md` §1 / §5–7, `karpathy-guidelines.mdc`, `pr-workflow.mdc` |
| Superpowers routing / install | `CLAUDE.md` §0, `superpowers.mdc`, `docs/superpowers/README.md`, `scripts/install-superpowers-skills.sh` |

## Upstream reference

[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) — keep principle files in sync when updating §1.
