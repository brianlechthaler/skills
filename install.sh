#!/usr/bin/env bash
# install.sh — install skills from this repo into popular AI coding tools
#
# Usage:
#   ./install.sh                          # interactive: pick skills and agents
#   ./install.sh --all                    # all skills, auto-detected agents
#   ./install.sh --all -a cursor -a claude-code -g
#   ./install.sh -s docker -a opencode --copy
#   ./install.sh -s docker -a cursor --as-rule
#   ./install.sh --all -a claude-code -a windsurf --as-rule -g -y
#   ./install.sh --list
#   ./install.sh --list-agents
#
# Run from a clone of this repo, or:
#   curl -sL https://raw.githubusercontent.com/brianlechthaler/skills/main/install.sh | bash -s -- --all -y

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SKILLS_REPO_ROOT:-$SCRIPT_DIR}"
TMP_REPO=""

cleanup() {
  if [[ -n "$TMP_REPO" && -d "$TMP_REPO" ]]; then
    rm -rf "$TMP_REPO"
  fi
}
trap cleanup EXIT

fetch_repo_if_needed() {
  mapfile -t _skills < <(discover_skills "$REPO_ROOT")
  [[ ${#_skills[@]} -gt 0 ]] && return 0

  local repo="${SKILLS_GITHUB_REPO:-brianlechthaler/skills}"
  local branch="${SKILLS_GITHUB_BRANCH:-main}"
  local tarball="https://github.com/${repo}/archive/refs/heads/${branch}.tar.gz"

  info "fetching skills from github.com/${repo} (${branch})..."
  TMP_REPO="$(mktemp -d)"
  curl -fsSL "$tarball" | tar -xz -C "$TMP_REPO" --strip-components=1
  REPO_ROOT="$TMP_REPO"
  if [[ "$METHOD" == "symlink" ]]; then
    info "using copy mode for remote install (symlinks would not persist)"
    METHOD="copy"
  fi
}

GLOBAL=0
METHOD="symlink"
YES=0
AS_RULE=0
SKILLS=()
AGENTS=()
INSTALL_ALL_SKILLS=0

err()  { echo "error: $*" >&2; exit 1; }
info() { echo "→ $*"; }
ok()   { echo "✓ $*"; }

usage() {
  cat <<'EOF'
Install skills from this repository into AI coding tool skill directories.

Usage:
  install.sh [options] [skill...]

Options:
  -h, --help           Show this help
  --list               List skills available in this repo
  --list-agents        List supported agents and install paths
  -s, --skill NAME     Install specific skill(s); repeatable
  --all                Install all skills in this repo
  -a, --agent NAME     Target agent(s); repeatable (see --list-agents)
  -g, --global         Install to user home dirs instead of current project
  --copy               Copy files instead of symlinking (default: symlink)
  --as-rule            Install as AI rules instead of skills (see --list-agents)
  -y, --yes            Skip confirmation prompts

Examples:
  ./install.sh --list
  ./install.sh --all -a cursor -a claude-code
  ./install.sh -s docker -g -a opencode -a codex -y
  ./install.sh -s test -a cursor --as-rule
  ./install.sh --all -a windsurf -a claude-code --as-rule -g -y
  ./install.sh --all --copy -g -y

Popular agents: cursor, claude-code, opencode, codex, windsurf, github-copilot,
gemini-cli, cline, roo, universal

Use --agent all to install to all supported agents.
EOF
}

# agent_id:project_relative:global_relative
# Paths are relative to project root or $HOME respectively.
AGENT_DEFS=(
  "cursor:.cursor/skills:~/.cursor/skills"
  "claude-code:.claude/skills:~/.claude/skills"
  "opencode:.opencode/skills:~/.config/opencode/skills"
  "codex:.codex/skills:~/.codex/skills"
  "windsurf:.windsurf/skills:~/.codeium/windsurf/skills"
  "github-copilot:.github/skills:~/.copilot/skills"
  "gemini-cli:.gemini/skills:~/.gemini/skills"
  "cline:.agents/skills:~/.agents/skills"
  "roo:.roo/skills:~/.roo/skills"
  "continue:.continue/skills:~/.continue/skills"
  "trae:.trae/skills:~/.trae/skills"
  "universal:.agents/skills:~/.agents/skills"
)

# agent_id:project_relative:global_relative:format:delivery
# delivery is per-file (one rule per skill) or append (section in a shared file)
RULE_DEFS=(
  "cursor:.cursor/rules:~/.cursor/rules:cursor:per-file"
  "claude-code:.claude/rules:~/.claude/rules:claude:per-file"
  "windsurf:.windsurf/rules:~/.codeium/windsurf/memories/global_rules.md:windsurf:per-file"
  "github-copilot:.github/copilot-instructions.md:~/.copilot/copilot-instructions.md:plain:append"
  "opencode:AGENTS.md:~/.opencode/AGENTS.md:plain:append"
  "codex:AGENTS.md:~/.codex/AGENTS.md:plain:append"
  "gemini-cli:GEMINI.md:~/.gemini/GEMINI.md:plain:append"
  "cline:.agents/rules:~/.agents/rules:plain:per-file"
  "roo:.roo/rules:~/.roo/rules:plain:per-file"
  "continue:.continue/rules:~/.continue/rules:plain:per-file"
  "trae:.trae/rules:~/.trae/rules:plain:per-file"
  "universal:.agents/rules:~/.agents/rules:plain:per-file"
)

agent_project_path() {
  local id="$1"
  local def id_part proj _global
  for def in "${AGENT_DEFS[@]}"; do
    IFS=':' read -r id_part proj _global <<<"$def"
    if [[ "$id_part" == "$id" ]]; then
      echo "$proj"
      return 0
    fi
  done
  return 1
}

agent_global_path() {
  local id="$1"
  local def id_part _proj global
  for def in "${AGENT_DEFS[@]}"; do
    IFS=':' read -r id_part _proj global <<<"$def"
    if [[ "$id_part" == "$id" ]]; then
      echo "$global"
      return 0
    fi
  done
  return 1
}

agent_exists() {
  local id="$1"
  agent_project_path "$id" >/dev/null 2>&1
}

rule_exists() {
  local id="$1" def id_part _rest
  for def in "${RULE_DEFS[@]}"; do
    IFS=':' read -r id_part _rest <<<"$def"
    if [[ "$id_part" == "$id" ]]; then
      return 0
    fi
  done
  return 1
}

rule_def_for_agent() {
  local id="$1"
  local def id_part proj global format delivery
  for def in "${RULE_DEFS[@]}"; do
    IFS=':' read -r id_part proj global format delivery <<<"$def"
    if [[ "$id_part" == "$id" ]]; then
      printf '%s:%s:%s:%s\n' "$proj" "$global" "$format" "$delivery"
      return 0
    fi
  done
  return 1
}

resolve_rule_target() {
  local id="$1"
  local proj global format delivery rel
  IFS=':' read -r proj global format delivery < <(rule_def_for_agent "$id") \
    || err "no rule mapping for agent: $id"

  if [[ "$GLOBAL" -eq 1 ]]; then
    case "$id" in
      windsurf)
        echo "${HOME}/.codeium/windsurf/memories/global_rules.md:append:windsurf"
        return 0
        ;;
    esac
    rel="$global"
    if [[ "$delivery" == "append" ]]; then
      echo "${rel/#\~/$HOME}:append:$format"
    else
      echo "${rel/#\~/$HOME}:per-file:$format"
    fi
  else
    case "$id" in
      windsurf)
        echo "$PWD/.windsurf/rules:per-file:windsurf"
        return 0
        ;;
    esac
    if [[ "$delivery" == "append" ]]; then
      echo "$PWD/$proj:append:$format"
    else
      echo "$PWD/$proj:per-file:$format"
    fi
  fi
}

rule_filename_for_skill() {
  local skill="$1" format="$2"
  case "$format" in
    cursor) echo "${skill}.mdc" ;;
    *) echo "${skill}.md" ;;
  esac
}

convert_skill_to_rule() {
  local skill_file="$1" format="$2"
  python3 - "$skill_file" "$format" <<'PY'
import re
import sys
from pathlib import Path

skill_file, fmt = sys.argv[1], sys.argv[2]
text = Path(skill_file).read_text()
match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)", text, re.DOTALL)
meta, body = {}, text
if match:
    frontmatter, body = match.group(1), match.group(2)
    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.M)
    if name_match:
        meta["name"] = name_match.group(1).strip().strip("\"'")
    desc_block = re.search(
        r"^description:\s*>?-?\s*\n((?:[ \t]+.+\n?)+)", frontmatter, re.M
    )
    if desc_block:
        meta["description"] = re.sub(
            r"\n[ \t]+", " ", desc_block.group(1)
        ).strip()
    else:
        desc_line = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
        if desc_line:
            meta["description"] = desc_line.group(1).strip().strip("\"'")

name = meta.get("name", Path(skill_file).parent.name)
description = meta.get("description", name)

if fmt == "cursor":
    print("---")
    print(f"description: {description}")
    print("alwaysApply: false")
    print("---")
    print(body, end="")
elif fmt == "claude":
    print("---")
    print("---")
    print(body, end="")
elif fmt == "windsurf":
    print("---")
    print("trigger: model_decision")
    print(f"description: {description}")
    print("---")
    print(body, end="")
else:
    title = name.replace("-", " ").title()
    print(f"# {title}")
    print()
    if description and description != name:
        print(f"> {description}")
        print()
    print(body, end="")
PY
}

upsert_marked_section() {
  local target="$1" skill="$2" content="$3"
  local begin="<!-- skills-install:${skill}:begin -->"
  local end="<!-- skills-install:${skill}:end -->"
  local tmp dir

  dir="$(dirname "$target")"
  mkdir -p "$dir"
  touch "$target"

  tmp="$(mktemp)"
  if grep -qF "$begin" "$target" 2>/dev/null; then
    awk -v begin="$begin" -v end="$end" '
      $0 ~ begin { skip=1; next }
      $0 ~ end { skip=0; next }
      !skip { print }
    ' "$target" >"$tmp"
  else
    cp "$target" "$tmp"
  fi

  {
    if [[ -s "$tmp" ]]; then
      tail -c1 "$tmp" | read -r _ || echo >>"$tmp"
      echo ""
    fi
    echo "$begin"
    printf '%s\n' "$content"
    echo "$end"
  } >>"$tmp"

  mv "$tmp" "$target"
}

all_agent_ids() {
  local def id_part _rest
  for def in "${AGENT_DEFS[@]}"; do
    IFS=':' read -r id_part _rest <<<"$def"
    echo "$id_part"
  done
}

resolve_agent_dir() {
  local id="$1"
  local rel
  if [[ "$GLOBAL" -eq 1 ]]; then
    rel="$(agent_global_path "$id")" || err "unknown agent: $id"
    echo "${rel/#\~/$HOME}"
  else
    rel="$(agent_project_path "$id")" || err "unknown agent: $id"
    echo "$PWD/$rel"
  fi
}

discover_skills() {
  local root="$1"
  local dir name
  shopt -s nullglob
  for dir in "$root"/*/; do
    name="$(basename "$dir")"
    [[ "$name" == .* ]] && continue
    [[ -f "${dir}SKILL.md" ]] || continue
    echo "$name"
  done
  shopt -u nullglob
}

list_skills() {
  mapfile -t found < <(discover_skills "$REPO_ROOT")
  if [[ ${#found[@]} -eq 0 ]]; then
    err "no skills found in $REPO_ROOT (expected <skill>/SKILL.md directories)"
  fi
  printf '%s\n' "${found[@]}"
}

list_agents() {
  local def id_part proj global
  printf "%-18s %-28s %s\n" "AGENT" "SKILL PROJECT" "SKILL GLOBAL"
  for def in "${AGENT_DEFS[@]}"; do
    IFS=':' read -r id_part proj global <<<"$def"
    printf "%-18s %-28s %s\n" "$id_part" "$proj" "$global"
  done
  echo ""
  printf "%-18s %-36s %s\n" "AGENT" "RULE PROJECT" "RULE GLOBAL"
  for def in "${RULE_DEFS[@]}"; do
    IFS=':' read -r id_part proj global _format _delivery <<<"$def"
    printf "%-18s %-36s %s\n" "$id_part" "$proj" "$global"
  done
  echo ""
  echo "Use --as-rule to install skills as rules instead of skill directories."
  echo "Windsurf global rules append to ~/.codeium/windsurf/memories/global_rules.md"
}

detect_agents() {
  local detected=()
  local id
  if [[ -d "$HOME/.cursor" ]] || command -v cursor >/dev/null 2>&1; then
    detected+=("cursor")
  fi
  if [[ -d "$HOME/.claude" ]] || command -v claude >/dev/null 2>&1; then
    detected+=("claude-code")
  fi
  if [[ -d "$HOME/.config/opencode" ]] || command -v opencode >/dev/null 2>&1; then
    detected+=("opencode")
  fi
  if [[ -d "$HOME/.codex" ]] || command -v codex >/dev/null 2>&1; then
    detected+=("codex")
  fi
  if [[ -d "$HOME/.codeium/windsurf" ]] || command -v windsurf >/dev/null 2>&1; then
    detected+=("windsurf")
  fi
  if [[ -d "$HOME/.copilot" ]]; then
    detected+=("github-copilot")
  fi
  if [[ -d "$HOME/.gemini" ]] || command -v gemini >/dev/null 2>&1; then
    detected+=("gemini-cli")
  fi
  if [[ ${#detected[@]} -eq 0 ]]; then
    detected=("cursor" "claude-code" "opencode")
  fi
  printf '%s\n' "${detected[@]}"
}

expand_agents() {
  local expanded=()
  local a id
  for a in "$@"; do
    if [[ "$a" == "all" ]]; then
      while IFS= read -r id; do
        expanded+=("$id")
      done < <(all_agent_ids)
    else
      if [[ "$AS_RULE" -eq 1 ]]; then
        rule_exists "$a" || err "unknown agent for --as-rule: $a (see --list-agents)"
      else
        agent_exists "$a" || err "unknown agent: $a (see --list-agents)"
      fi
      expanded+=("$a")
    fi
  done
  AGENTS=("${expanded[@]}")
}

expand_skills() {
  mapfile -t available < <(list_skills)
  if [[ "$INSTALL_ALL_SKILLS" -eq 1 ]]; then
    SKILLS=("${available[@]}")
    return
  fi
  if [[ ${#SKILLS[@]} -eq 0 ]]; then
    SKILLS=("${available[@]}")
    return
  fi
  local want avail
  for want in "${SKILLS[@]}"; do
    for avail in "${available[@]}"; do
      if [[ "$want" == "$avail" ]]; then
        continue 2
      fi
    done
    err "unknown skill: $want (see --list)"
  done
}

install_skill_for_agent() {
  local skill="$1"
  local agent="$2"
  local src="$REPO_ROOT/$skill"
  local agent_dir dest

  [[ -d "$src" && -f "$src/SKILL.md" ]] || err "missing skill source: $src"

  agent_dir="$(resolve_agent_dir "$agent")"
  dest="$agent_dir/$skill"
  mkdir -p "$agent_dir"

  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$METHOD" == "symlink" && -L "$dest" ]]; then
      rm "$dest"
    elif [[ -d "$dest" ]]; then
      info "$agent: replacing existing $dest"
      rm -rf "$dest"
    else
      rm -f "$dest"
    fi
  fi

  if [[ "$METHOD" == "copy" ]]; then
    cp -R "$src" "$dest"
  else
    ln -s "$src" "$dest"
  fi

  find "$dest" -type f -name '*.sh' -exec chmod +x {} + 2>/dev/null || true
  ok "$skill -> $dest ($agent)"
}

install_skill_as_rule_for_agent() {
  local skill="$1"
  local agent="$2"
  local src="$REPO_ROOT/$skill/SKILL.md"
  local target_spec delivery format target_dir target_file content filename

  [[ -f "$src" ]] || err "missing skill source: $src"

  IFS=':' read -r target_spec delivery format < <(resolve_rule_target "$agent")
  content="$(convert_skill_to_rule "$src" "$format")"

  if [[ "$delivery" == "append" ]]; then
    upsert_marked_section "$target_spec" "$skill" "$content"
    ok "$skill -> $target_spec ($agent rule)"
    return 0
  fi

  target_dir="$target_spec"
  filename="$(rule_filename_for_skill "$skill" "$format")"
  target_file="$target_dir/$filename"
  mkdir -p "$target_dir"
  printf '%s\n' "$content" >"$target_file"
  ok "$skill -> $target_file ($agent rule)"
}

confirm() {
  [[ "$YES" -eq 1 ]] && return 0
  local reply
  read -r -p "$1 [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]]
}

ACTION="install"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --list) ACTION="list"; shift ;;
    --list-agents) ACTION="list-agents"; shift ;;
    --all) INSTALL_ALL_SKILLS=1; shift ;;
    -g|--global) GLOBAL=1; shift ;;
    --copy) METHOD="copy"; shift ;;
    --as-rule) AS_RULE=1; METHOD="copy"; shift ;;
    -y|--yes) YES=1; shift ;;
    -s|--skill) [[ -n "${2:-}" ]] || err "missing value for $1"; SKILLS+=("$2"); shift 2 ;;
    -a|--agent) [[ -n "${2:-}" ]] || err "missing value for $1"; AGENTS+=("$2"); shift 2 ;;
    -*) err "unknown option: $1" ;;
    *) SKILLS+=("$1"); shift ;;
  esac
done

[[ -d "$REPO_ROOT" ]] || err "repo root not found: $REPO_ROOT"

if [[ "$ACTION" == "list-agents" ]]; then
  list_agents
  exit 0
fi

if [[ "$ACTION" == "list" ]]; then
  fetch_repo_if_needed
  list_skills
  exit 0
fi

fetch_repo_if_needed

expand_skills

if [[ ${#AGENTS[@]} -eq 0 ]]; then
  mapfile -t AGENTS < <(detect_agents)
  info "auto-detected agents: ${AGENTS[*]}"
fi

expand_agents "${AGENTS[@]}"

scope="project ($(pwd))"
[[ "$GLOBAL" -eq 1 ]] && scope="global ($HOME)"

install_mode="skills"
[[ "$AS_RULE" -eq 1 ]] && install_mode="rules"

echo ""
echo "Skills : ${SKILLS[*]}"
echo "Agents : ${AGENTS[*]}"
echo "Scope  : $scope"
echo "Mode   : $install_mode"
[[ "$AS_RULE" -eq 0 ]] && echo "Method : $METHOD"
echo ""

confirm "Proceed with installation?" || { echo "cancelled."; exit 0; }

for agent in "${AGENTS[@]}"; do
  for skill in "${SKILLS[@]}"; do
    if [[ "$AS_RULE" -eq 1 ]]; then
      install_skill_as_rule_for_agent "$skill" "$agent"
    else
      install_skill_for_agent "$skill" "$agent"
    fi
  done
done

echo ""
if [[ "$AS_RULE" -eq 1 ]]; then
  ok "installed ${#SKILLS[@]} rule(s) to ${#AGENTS[@]} agent(s)."
else
  ok "installed ${#SKILLS[@]} skill(s) to ${#AGENTS[@]} agent(s)."
fi
echo "Restart your coding tool or start a new session to pick up changes."
