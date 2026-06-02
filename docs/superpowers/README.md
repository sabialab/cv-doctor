# Superpowers in CV-Doctor

[Superpowers](https://github.com/obra/superpowers) is the **skill workflow** for brainstorming → plans → TDD → verify-before-done.

## Install (Cursor — required)

1. Open **Agent** chat (`Cmd+L` / `Ctrl+L`), not Composer-only inline chat.
2. Run:

```text
/plugin-add superpowers
```

3. Update when needed:

```text
/plugin-update superpowers
```

4. **Verify:** new Agent session → ask: `Do you have superpowers?`  
   Or: `Use the brainstorming skill before we plan M2.`

Plugin cache on this machine is typically:

`~/.cursor/plugins/cache/cursor-public/superpowers/<hash>/`

## Fallback: link skills into `~/.cursor/skills`

If the plugin is installed but skills are not discoverable, from repo root:

```bash
chmod +x scripts/install-superpowers-skills.sh
./scripts/install-superpowers-skills.sh
```

Override source:

```bash
git clone --depth 1 https://github.com/obra/superpowers.git /tmp/superpowers
SUPERPOWERS_SKILLS_SRC=/tmp/superpowers/skills ./scripts/install-superpowers-skills.sh
```

## Repo conventions (this project)

| Path | Purpose |
|------|---------|
| `docs/superpowers/specs/` | Approved design specs (`brainstorming` output) |
| `docs/superpowers/plans/` | Implementation plans (`writing-plans` output); **active:** [2026-06-01-p0-m2-frontend-closure.md](./plans/2026-06-01-p0-m2-frontend-closure.md) |
| `.cursor/rules/superpowers.mdc` | Skill routing (always apply) |
| `CLAUDE.md` §0 | When to call which skill |

**Do not** put ad-hoc plans only in `docs/p0-*.md` without the Superpowers header/checkbox task format — use `docs/superpowers/plans/`.

## Priority

1. User explicit instruction  
2. `CLAUDE.md` §1 Karpathy  
3. Superpowers skills  
4. Product/trust (`§2–3`)
