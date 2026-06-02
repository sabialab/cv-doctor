#!/usr/bin/env bash
# Sync Superpowers skills into ~/.cursor/skills for @-mention / fallback when the
# Cursor plugin Skill tool is unavailable. Primary install: Agent chat → /plugin-add superpowers
set -euo pipefail

SKILLS_HOME="${CURSOR_SKILLS_HOME:-$HOME/.cursor/skills}"
resolve_source() {
  if [[ -n "${SUPERPOWERS_SKILLS_SRC:-}" && -d "${SUPERPOWERS_SKILLS_SRC}" ]]; then
    echo "${SUPERPOWERS_SKILLS_SRC}"
    return 0
  fi
  local newest
  newest="$(ls -dt "$HOME"/.cursor/plugins/cache/cursor-public/superpowers/*/skills 2>/dev/null | head -1)"
  if [[ -z "$newest" || ! -d "$newest" ]]; then
    return 1
  fi
  echo "$newest"
}

SOURCE="$(resolve_source)" || {
  echo "Superpowers skills not found." >&2
  echo "Install the Cursor plugin first (Agent chat):" >&2
  echo "  /plugin-add superpowers" >&2
  echo "Then re-run this script, or set SUPERPOWERS_SKILLS_SRC to a clone of https://github.com/obra/superpowers/skills" >&2
  exit 1
}

mkdir -p "$SKILLS_HOME"
linked=0
for skill_dir in "$SOURCE"/*/; do
  name="$(basename "$skill_dir")"
  target="$SKILLS_HOME/$name"
  if [[ -L "$target" ]]; then
    rm "$target"
  elif [[ -d "$target" && ! -L "$target" ]]; then
    echo "Skip $name (exists and is not a symlink: $target)" >&2
    continue
  fi
  ln -sfn "$skill_dir" "$target"
  linked=$((linked + 1))
done

echo "Linked $linked Superpowers skills from:"
echo "  $SOURCE"
echo "Into:"
echo "  $SKILLS_HOME"
echo ""
echo "Verify in Cursor Agent: ask 'Do you have superpowers?' or request 'use the brainstorming skill'."
