#!/usr/bin/env bash
# install.sh — install skills from this repo into popular AI coding tools
#
# Usage:
#   ./install.sh                          # interactive: pick skills and agents
#   ./install.sh --all                    # all skills, auto-detected agents
#   ./install.sh --all -a cursor -a claude-code -g
#   ./install.sh -s docker -a opencode --copy
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
  -y, --yes            Skip confirmation prompts

Examples:
  ./install.sh --list
  ./install.sh --all -a cursor -a claude-code
  ./install.sh -s docker -g -a opencode -a codex -y
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
  printf "%-18s %-28s %s\n" "AGENT" "PROJECT PATH" "GLOBAL PATH"
  for def in "${AGENT_DEFS[@]}"; do
    IFS=':' read -r id_part proj global <<<"$def"
    printf "%-18s %-28s %s\n" "$id_part" "$proj" "$global"
  done
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
      agent_exists "$a" || err "unknown agent: $a (see --list-agents)"
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

echo ""
echo "Skills : ${SKILLS[*]}"
echo "Agents : ${AGENTS[*]}"
echo "Scope  : $scope"
echo "Method : $METHOD"
echo ""

confirm "Proceed with installation?" || { echo "cancelled."; exit 0; }

for agent in "${AGENTS[@]}"; do
  for skill in "${SKILLS[@]}"; do
    install_skill_for_agent "$skill" "$agent"
  done
done

echo ""
ok "installed ${#SKILLS[@]} skill(s) to ${#AGENTS[@]} agent(s)."
echo "Restart your coding tool or start a new session to pick up changes."
