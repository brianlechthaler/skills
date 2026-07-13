#!/usr/bin/env python3
"""Install skills from this repository into popular AI coding tools."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import sys
import tarfile
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from skill_categories import SKILL_CATEGORIES, validate_skill_categories

DEFAULT_GITHUB_REPO = "brianlechthaler/skills"
DEFAULT_GITHUB_BRANCH = "main"
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ALLOWED_TARBALL_HOSTS = frozenset({"github.com", "www.github.com"})

Format = Literal["cursor", "claude", "windsurf", "plain"]
Delivery = Literal["per-file", "append"]
Method = Literal["symlink", "copy"]


@dataclass(frozen=True)
class AgentDef:
    id: str
    project: str
    global_path: str


@dataclass(frozen=True)
class RuleDef:
    id: str
    project: str
    global_path: str
    format: Format
    delivery: Delivery


AGENT_DEFS: tuple[AgentDef, ...] = (
    AgentDef("cursor", ".cursor/skills", "~/.cursor/skills"),
    AgentDef("claude-code", ".claude/skills", "~/.claude/skills"),
    AgentDef("opencode", ".opencode/skills", "~/.config/opencode/skills"),
    AgentDef("codex", ".codex/skills", "~/.codex/skills"),
    AgentDef("windsurf", ".windsurf/skills", "~/.codeium/windsurf/skills"),
    AgentDef("github-copilot", ".github/skills", "~/.copilot/skills"),
    AgentDef("gemini-cli", ".gemini/skills", "~/.gemini/skills"),
    AgentDef("openclaw", "skills", "~/.openclaw/skills"),
    AgentDef("hermes-agent", ".hermes/skills", "~/.hermes/skills"),
    AgentDef("mistral-vibe", ".vibe/skills", "~/.vibe/skills"),
    AgentDef("aider", ".aider/skills", "~/.aider/skills"),
    AgentDef("kilo-code", ".kilo/skills", "~/.kilo/skills"),
    AgentDef("augment", ".augment/skills", "~/.augment/skills"),
    AgentDef("antigravity", ".agents/skills", "~/.gemini/antigravity/skills"),
    AgentDef("cline", ".agents/skills", "~/.agents/skills"),
    AgentDef("roo", ".roo/skills", "~/.roo/skills"),
    AgentDef("continue", ".continue/skills", "~/.continue/skills"),
    AgentDef("trae", ".trae/skills", "~/.trae/skills"),
    AgentDef("universal", ".agents/skills", "~/.agents/skills"),
)

RULE_DEFS: tuple[RuleDef, ...] = (
    RuleDef("cursor", ".cursor/rules", "~/.cursor/rules", "cursor", "per-file"),
    RuleDef("claude-code", ".claude/rules", "~/.claude/rules", "claude", "per-file"),
    RuleDef(
        "windsurf",
        ".windsurf/rules",
        "~/.codeium/windsurf/memories/global_rules.md",
        "windsurf",
        "per-file",
    ),
    RuleDef(
        "github-copilot",
        ".github/copilot-instructions.md",
        "~/.copilot/copilot-instructions.md",
        "plain",
        "append",
    ),
    RuleDef("opencode", "AGENTS.md", "~/.opencode/AGENTS.md", "plain", "append"),
    RuleDef("codex", "AGENTS.md", "~/.codex/AGENTS.md", "plain", "append"),
    RuleDef("gemini-cli", "GEMINI.md", "~/.gemini/GEMINI.md", "plain", "append"),
    RuleDef("openclaw", ".agents/rules", "~/.agents/rules", "plain", "per-file"),
    RuleDef("hermes-agent", ".hermes/rules", "~/.hermes/rules", "plain", "per-file"),
    RuleDef("mistral-vibe", ".vibe/rules", "~/.vibe/rules", "plain", "per-file"),
    RuleDef("aider", "CONVENTIONS.md", "~/.aider/CONVENTIONS.md", "plain", "append"),
    RuleDef("kilo-code", "AGENTS.md", "~/.config/kilo/AGENTS.md", "plain", "append"),
    RuleDef("augment", ".augment/rules", "~/.augment/rules", "plain", "per-file"),
    RuleDef("antigravity", ".agents/rules", "~/.agents/rules", "plain", "per-file"),
    RuleDef("cline", ".agents/rules", "~/.agents/rules", "plain", "per-file"),
    RuleDef("roo", ".roo/rules", "~/.roo/rules", "plain", "per-file"),
    RuleDef("continue", ".continue/rules", "~/.continue/rules", "plain", "per-file"),
    RuleDef("trae", ".trae/rules", "~/.trae/rules", "plain", "per-file"),
    RuleDef("universal", ".agents/rules", "~/.agents/rules", "plain", "per-file"),
)


@dataclass
class InstallOptions:
    repo_root: Path
    global_install: bool = False
    method: Method = "symlink"
    yes: bool = False
    as_rule: bool = False
    skills: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    install_all_skills: bool = False
    project_dir: Path = field(default_factory=Path.cwd)
    home_dir: Path = field(default_factory=Path.home)
    tmp_repo: Path | None = None


def err(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def info(message: str) -> None:
    print(f"→ {message}")


def ok(message: str) -> None:
    print(f"✓ {message}")


def expand_home(path: str, home: Path) -> Path:
    if path.startswith("~/"):
        return home / path[2:]
    return Path(path)


def agent_by_id(agent_id: str) -> AgentDef | None:
    for agent in AGENT_DEFS:
        if agent.id == agent_id:
            return agent
    return None


def rule_by_id(agent_id: str) -> RuleDef | None:
    for rule in RULE_DEFS:
        if rule.id == agent_id:
            return rule
    return None


def all_agent_ids() -> list[str]:
    return [agent.id for agent in AGENT_DEFS]


def validate_skill_name(name: str) -> None:
    if not SKILL_NAME_RE.match(name):
        err(f"invalid skill name: {name}")


def validate_agent_id(agent_id: str, as_rule: bool) -> None:
    if agent_id == "all":
        return
    if as_rule:
        if rule_by_id(agent_id) is None:
            err(f"unknown agent for --as-rule: {agent_id} (see --list-agents)")
    elif agent_by_id(agent_id) is None:
        err(f"unknown agent: {agent_id} (see --list-agents)")


def discover_skills(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    found: list[str] = []
    for entry in sorted(root.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        if (entry / "SKILL.md").is_file():
            found.append(entry.name)
    return found


def list_skills(root: Path) -> list[str]:
    found = discover_skills(root)
    if not found:
        err(f"no skills found in {root} (expected <skill>/SKILL.md directories)")
    return found


def list_skills_by_category(root: Path) -> None:
    found = list_skills(root)
    validate_skill_categories(found)
    found_set = set(found)
    for category, skills in SKILL_CATEGORIES:
        category_skills = [skill for skill in skills if skill in found_set]
        print(f"{category} ({len(category_skills)})")
        for skill in category_skills:
            print(f"  {skill}")
        print()


def list_agents() -> None:
    print(f"{'AGENT':<18} {'SKILL PROJECT':<28} SKILL GLOBAL")
    for agent in AGENT_DEFS:
        print(f"{agent.id:<18} {agent.project:<28} {agent.global_path}")
    print()
    print(f"{'AGENT':<18} {'RULE PROJECT':<36} RULE GLOBAL")
    for rule in RULE_DEFS:
        print(f"{rule.id:<18} {rule.project:<36} {rule.global_path}")
    print()
    print("Use --as-rule to install skills as rules instead of skill directories.")
    print(
        "Windsurf global rules append to ~/.codeium/windsurf/memories/global_rules.md"
    )


def resolve_agent_dir(options: InstallOptions, agent_id: str) -> Path:
    agent = agent_by_id(agent_id)
    if agent is None:
        err(f"unknown agent: {agent_id}")
    if options.global_install:
        return expand_home(agent.global_path, options.home_dir)
    return options.project_dir / agent.project


def resolve_rule_target(
    options: InstallOptions, agent_id: str
) -> tuple[Path, Delivery, Format]:
    rule = rule_by_id(agent_id)
    if rule is None:
        err(f"no rule mapping for agent: {agent_id}")

    if options.global_install:
        if agent_id == "windsurf":
            target = options.home_dir / ".codeium/windsurf/memories/global_rules.md"
            return target, "append", "windsurf"
        target = expand_home(rule.global_path, options.home_dir)
        return target, rule.delivery, rule.format

    if agent_id == "windsurf":
        return options.project_dir / ".windsurf/rules", "per-file", "windsurf"

    if rule.delivery == "append":
        return options.project_dir / rule.project, "append", rule.format
    return options.project_dir / rule.project, "per-file", rule.format


def rule_filename_for_skill(skill: str, fmt: Format) -> str:
    if fmt == "cursor":
        return f"{skill}.mdc"
    return f"{skill}.md"


def parse_skill_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text

    frontmatter, body = match.group(1), match.group(2)
    meta: dict[str, str] = {}

    name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
    if name_match:
        meta["name"] = name_match.group(1).strip().strip("\"'")

    desc_block = re.search(
        r"^description:\s*>?-?\s*\n((?:[ \t]+.+\n?)+)", frontmatter, re.MULTILINE
    )
    if desc_block:
        meta["description"] = re.sub(r"\n[ \t]+", " ", desc_block.group(1)).strip()
    else:
        desc_line = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        if desc_line:
            meta["description"] = desc_line.group(1).strip().strip("\"'")

    return meta, body


def convert_skill_to_rule(skill_file: Path, fmt: Format) -> str:
    text = skill_file.read_text(encoding="utf-8")
    meta, body = parse_skill_frontmatter(text)
    name = meta.get("name", skill_file.parent.name)
    description = meta.get("description", name)

    if fmt == "cursor":
        return f"---\ndescription: {description}\nalwaysApply: false\n---\n{body}"
    if fmt == "claude":
        return f"---\n---\n{body}"
    if fmt == "windsurf":
        return f"---\ntrigger: model_decision\ndescription: {description}\n---\n{body}"

    title = name.replace("-", " ").title()
    lines = [f"# {title}", ""]
    if description and description != name:
        lines.extend([f"> {description}", ""])
    lines.append(body.rstrip("\n") if body else "")
    return "\n".join(lines) + ("\n" if body.endswith("\n") else "")


def upsert_marked_section(target: Path, skill: str, content: str) -> None:
    begin = f"<!-- skills-install:{skill}:begin -->"
    end = f"<!-- skills-install:{skill}:end -->"

    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.touch()

    existing = target.read_text(encoding="utf-8")
    if begin in existing:
        pattern = re.compile(
            re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.DOTALL
        )
        existing = pattern.sub("", existing)

    section_parts: list[str] = []
    if existing:
        if not existing.endswith("\n"):
            existing += "\n"
        section_parts.append(existing)
        section_parts.append("\n")
    section_parts.extend([begin + "\n", content.rstrip("\n") + "\n", end + "\n"])
    target.write_text("".join(section_parts), encoding="utf-8")


def command_on_path(name: str) -> bool:
    return shutil.which(name) is not None


def detect_agents(home: Path) -> list[str]:
    detected: list[str] = []
    checks: list[tuple[str, list[Path], str | None]] = [
        ("cursor", [home / ".cursor"], "cursor"),
        ("claude-code", [home / ".claude"], "claude"),
        ("opencode", [home / ".config/opencode"], "opencode"),
        ("codex", [home / ".codex"], "codex"),
        ("windsurf", [home / ".codeium/windsurf"], "windsurf"),
        ("github-copilot", [home / ".copilot"], None),
        ("gemini-cli", [home / ".gemini"], "gemini"),
        ("openclaw", [home / ".openclaw"], "openclaw"),
        ("hermes-agent", [home / ".hermes"], "hermes"),
        ("mistral-vibe", [home / ".vibe"], "vibe"),
        ("aider", [home / ".aider"], "aider"),
        ("kilo-code", [home / ".kilo", home / ".kilocode"], None),
        ("augment", [home / ".augment"], None),
        (
            "antigravity",
            [home / ".gemini/antigravity", home / ".gemini/antigravity-cli"],
            None,
        ),
    ]
    for agent_id, dirs, cmd in checks:
        if any(path.is_dir() for path in dirs):
            detected.append(agent_id)
        elif cmd and command_on_path(cmd):
            detected.append(agent_id)

    if not detected:
        return ["cursor", "claude-code", "opencode"]
    return detected


def expand_agents(agents: list[str], as_rule: bool) -> list[str]:
    expanded: list[str] = []
    for agent_id in agents:
        if agent_id == "all":
            expanded.extend(all_agent_ids())
        else:
            validate_agent_id(agent_id, as_rule)
            expanded.append(agent_id)
    return expanded


def expand_skills(options: InstallOptions) -> list[str]:
    available = list_skills(options.repo_root)
    if options.install_all_skills or not options.skills:
        return available
    for want in options.skills:
        validate_skill_name(want)
        if want not in available:
            err(f"unknown skill: {want} (see --list)")
    return options.skills


def validate_tarball_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        err(f"refusing non-https tarball URL: {url}")
    if parsed.netloc not in ALLOWED_TARBALL_HOSTS:
        err(f"refusing tarball from untrusted host: {parsed.netloc}")


def safe_extract_tar(tar: tarfile.TarFile, dest: Path) -> None:
    dest_resolved = dest.resolve()
    for member in tar.getmembers():
        member_path = (dest / member.name).resolve()
        if member_path != dest_resolved and not str(member_path).startswith(
            str(dest_resolved) + os.sep
        ):
            err(f"unsafe path in archive: {member.name}")
    if sys.version_info >= (3, 12):
        tar.extractall(dest, filter="data")
    else:
        tar.extractall(dest)  # noqa: S202 — member paths validated above


def fetch_repo_if_needed(options: InstallOptions) -> None:
    if discover_skills(options.repo_root):
        return

    repo = os.environ.get("SKILLS_GITHUB_REPO", DEFAULT_GITHUB_REPO)
    branch = os.environ.get("SKILLS_GITHUB_BRANCH", DEFAULT_GITHUB_BRANCH)
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo) or ".." in repo:
        err(f"invalid SKILLS_GITHUB_REPO: {repo}")
    if not re.fullmatch(r"[\w./-]+", branch) or ".." in branch:
        err(f"invalid SKILLS_GITHUB_BRANCH: {branch}")

    tarball_url = f"https://github.com/{repo}/archive/refs/heads/{branch}.tar.gz"
    validate_tarball_url(tarball_url)

    info(f"fetching skills from github.com/{repo} ({branch})...")
    tmp_repo = Path(tempfile.mkdtemp(prefix="skills-install-"))
    options.tmp_repo = tmp_repo

    try:
        with urlopen(tarball_url, timeout=60) as response:  # noqa: S310
            archive_path = tmp_repo / "archive.tar.gz"
            archive_path.write_bytes(response.read())
        with tarfile.open(archive_path, "r:gz") as tar:
            safe_extract_tar(tar, tmp_repo)
        archive_path.unlink(missing_ok=True)

        extracted_root = tmp_repo
        subdirs = [p for p in tmp_repo.iterdir() if p.is_dir()]
        if len(subdirs) == 1:
            extracted_root = subdirs[0]

        options.repo_root = extracted_root
    except (URLError, OSError, tarfile.TarError) as exc:
        err(f"failed to fetch skills: {exc}")

    if options.method == "symlink":
        info("using copy mode for remote install (symlinks would not persist)")
        options.method = "copy"


def cleanup(options: InstallOptions) -> None:
    if options.tmp_repo and options.tmp_repo.is_dir():
        shutil.rmtree(options.tmp_repo, ignore_errors=True)
        options.tmp_repo = None


def make_executable_sh_files(dest: Path) -> None:
    if os.name == "nt":
        return
    for sh_file in dest.rglob("*.sh"):
        if sh_file.is_file():
            mode = sh_file.stat().st_mode
            sh_file.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def remove_destination(dest: Path) -> None:
    if not dest.exists() and not dest.is_symlink():
        return
    if dest.is_symlink():
        dest.unlink()
    elif dest.is_dir():
        info(f"replacing existing {dest}")
        shutil.rmtree(dest)
    else:
        dest.unlink()


def install_skill_for_agent(options: InstallOptions, skill: str, agent_id: str) -> None:
    validate_skill_name(skill)
    src = options.repo_root / skill
    skill_file = src / "SKILL.md"
    if not skill_file.is_file():
        err(f"missing skill source: {src}")

    agent_dir = resolve_agent_dir(options, agent_id)
    dest = agent_dir / skill
    agent_dir.mkdir(parents=True, exist_ok=True)
    remove_destination(dest)

    if options.method == "copy":
        shutil.copytree(src, dest)
    else:
        try:
            dest.symlink_to(src.resolve())
        except OSError as exc:
            info(f"symlink failed, using copy: {exc}")
            shutil.copytree(src, dest)

    make_executable_sh_files(dest)
    ok(f"{skill} -> {dest} ({agent_id})")


def install_skill_as_rule_for_agent(
    options: InstallOptions, skill: str, agent_id: str
) -> None:
    validate_skill_name(skill)
    src = options.repo_root / skill / "SKILL.md"
    if not src.is_file():
        err(f"missing skill source: {src}")

    target, delivery, fmt = resolve_rule_target(options, agent_id)
    content = convert_skill_to_rule(src, fmt)

    if delivery == "append":
        upsert_marked_section(target, skill, content)
        ok(f"{skill} -> {target} ({agent_id} rule)")
        return

    filename = rule_filename_for_skill(skill, fmt)
    target_file = target / filename
    target.mkdir(parents=True, exist_ok=True)
    target_file.write_text(content, encoding="utf-8")
    ok(f"{skill} -> {target_file} ({agent_id} rule)")


def confirm(prompt: str, yes: bool) -> bool:
    if yes:
        return True
    reply = input(f"{prompt} [y/N] ").strip()
    return reply.lower() in {"y", "yes"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Install skills from this repository into AI coding tool skill directories."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Popular agents: cursor, claude-code, opencode, codex, windsurf, "
            "gemini-cli, openclaw, hermes-agent, mistral-vibe, aider, kilo-code, "
            "augment, antigravity, github-copilot, cline, roo, universal\n\n"
            "Use --agent all to install to all supported agents."
        ),
    )
    parser.add_argument("--list", action="store_true", help="List skills in this repo")
    parser.add_argument(
        "--list-by-category",
        action="store_true",
        help="List skills grouped by high-level category",
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="List supported agents and install paths",
    )
    parser.add_argument(
        "-s",
        "--skill",
        action="append",
        default=[],
        dest="skills",
        help="Install skill(s)",
    )
    parser.add_argument(
        "--all", action="store_true", dest="install_all", help="Install all skills"
    )
    parser.add_argument(
        "-a",
        "--agent",
        action="append",
        default=[],
        dest="agents",
        help="Target agent(s)",
    )
    parser.add_argument(
        "-g",
        "--global",
        action="store_true",
        dest="global_install",
        help="Install to home dirs",
    )
    parser.add_argument(
        "--copy", action="store_true", help="Copy files instead of symlinking"
    )
    parser.add_argument(
        "--as-rule", action="store_true", help="Install as AI rules instead of skills"
    )
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompts"
    )
    parser.add_argument("positional_skills", nargs="*", help="Skill names")
    return parser


def run_install(options: InstallOptions) -> int:
    try:
        fetch_repo_if_needed(options)
        skills = expand_skills(options)
        agents = options.agents or detect_agents(options.home_dir)
        if not options.agents:
            info(f"auto-detected agents: {' '.join(agents)}")
        agents = expand_agents(agents, options.as_rule)

        scope = (
            f"global ({options.home_dir})"
            if options.global_install
            else f"project ({options.project_dir})"
        )
        install_mode = "rules" if options.as_rule else "skills"

        print()
        print(f"Skills : {' '.join(skills)}")
        print(f"Agents : {' '.join(agents)}")
        print(f"Scope  : {scope}")
        print(f"Mode   : {install_mode}")
        if not options.as_rule:
            print(f"Method : {options.method}")
        print()

        if not confirm("Proceed with installation?", options.yes):
            print("cancelled.")
            return 0

        for agent_id in agents:
            for skill in skills:
                if options.as_rule:
                    install_skill_as_rule_for_agent(options, skill, agent_id)
                else:
                    install_skill_for_agent(options, skill, agent_id)

        print()
        noun = "rule(s)" if options.as_rule else "skill(s)"
        ok(f"installed {len(skills)} {noun} to {len(agents)} agent(s).")
        print("Restart your coding tool or start a new session to pick up changes.")
        return 0
    finally:
        cleanup(options)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    script_dir = Path(__file__).resolve().parent
    repo_root = Path(os.environ.get("SKILLS_REPO_ROOT", script_dir))

    if args.list_agents:
        list_agents()
        return 0

    if not repo_root.is_dir():
        err(f"repo root not found: {repo_root}")

    options = InstallOptions(
        repo_root=repo_root,
        global_install=args.global_install,
        method="copy" if args.copy or args.as_rule else "symlink",
        yes=args.yes,
        as_rule=args.as_rule,
        skills=[*args.skills, *args.positional_skills],
        agents=args.agents,
        install_all_skills=args.install_all,
    )

    if args.list or args.list_by_category:
        try:
            fetch_repo_if_needed(options)
            if args.list_by_category:
                list_skills_by_category(options.repo_root)
            else:
                for skill in list_skills(options.repo_root):
                    print(skill)
        finally:
            cleanup(options)
        return 0

    return run_install(options)


if __name__ == "__main__":
    sys.exit(main())
