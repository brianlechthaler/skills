"""Validate skill directories in this repository."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import install

MARKDOWN_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#\s+\S", re.MULTILINE)
FENCED_CODE_RE = re.compile(r"```[\s\S]*?```")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
DOUBLE_INLINE_CODE_RE = re.compile(r"``[^`\n]+``")
README_SKILL_LINK_RE = re.compile(
    r"\[([a-z0-9][a-z0-9-]*)\]\(([a-z0-9][a-z0-9-]*)/SKILL\.md\)"
)
MIN_BODY_CHARS = 100
MIN_DESCRIPTION_CHARS = 20
RULE_FORMATS: tuple[install.Format, ...] = ("cursor", "claude", "windsurf", "plain")


@dataclass
class SkillValidationResult:
    skill: str
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def strip_code_literals(text: str) -> str:
    without_double_inline = DOUBLE_INLINE_CODE_RE.sub("", text)
    without_inline = INLINE_CODE_RE.sub("", without_double_inline)
    return FENCED_CODE_RE.sub("", without_inline)


def validate_skill_frontmatter(skill: str, meta: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if not meta:
        errors.append("missing YAML frontmatter")
        return errors

    name = meta.get("name", "")
    if not name:
        errors.append("missing frontmatter field: name")
    elif name != skill:
        errors.append(f"name {name!r} does not match directory {skill!r}")
    elif not install.SKILL_NAME_RE.match(name):
        errors.append(f"invalid skill name: {name!r}")

    description = meta.get("description", "")
    if not description:
        errors.append("missing frontmatter field: description")
    elif len(description) < MIN_DESCRIPTION_CHARS:
        errors.append(
            f"description too short ({len(description)} chars, "
            f"min {MIN_DESCRIPTION_CHARS})"
        )
    return errors


def resolve_markdown_link(skill_dir: Path, target: str) -> Path:
    path_part = target.split("#", 1)[0]
    return (skill_dir / path_part).resolve()


def validate_markdown_links(
    skill_dir: Path,
    text: str,
    known_skills: frozenset[str],
) -> list[str]:
    errors: list[str] = []
    check_text = strip_code_literals(text)

    for match in MARKDOWN_LINK_RE.finditer(check_text):
        target = match.group(2).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if target.startswith("~"):
            continue

        if target.startswith("../") and target.endswith("/SKILL.md"):
            ref_skill = Path(target).parts[1]
            if ref_skill not in known_skills:
                errors.append(f"broken cross-skill link: {target!r}")
            continue

        if target.startswith("../"):
            resolved = resolve_markdown_link(skill_dir, target)
            if not resolved.is_file():
                errors.append(f"broken parent-relative link: {target!r}")
            continue

        resolved = resolve_markdown_link(skill_dir, target)
        if not resolved.is_file():
            errors.append(f"broken local link: {target!r}")

    return errors


def validate_skill_body(body: str) -> list[str]:
    errors: list[str] = []
    stripped = body.strip()
    if not stripped:
        errors.append("empty skill body after frontmatter")
    elif len(stripped) < MIN_BODY_CHARS:
        errors.append(f"body too short ({len(stripped)} chars, min {MIN_BODY_CHARS})")
    if not HEADING_RE.search(body):
        errors.append("body missing top-level markdown heading (# ...)")
    return errors


def validate_rule_conversion(skill_file: Path) -> list[str]:
    errors: list[str] = []
    for fmt in RULE_FORMATS:
        try:
            converted = install.convert_skill_to_rule(skill_file, fmt)
        except OSError as exc:
            errors.append(f"rule conversion to {fmt} failed: {exc}")
            continue
        if not converted.strip():
            errors.append(f"rule conversion to {fmt} produced empty output")
    return errors


def validate_skill(
    skill: str,
    repo_root: Path,
    known_skills: frozenset[str] | None = None,
) -> SkillValidationResult:
    if known_skills is None:
        known_skills = frozenset(install.discover_skills(repo_root))

    skill_dir = repo_root / skill
    skill_file = skill_dir / "SKILL.md"
    result = SkillValidationResult(skill=skill)

    if not skill_file.is_file():
        result.errors.append("SKILL.md not found")
        return result

    text = skill_file.read_text(encoding="utf-8")
    meta, body = install.parse_skill_frontmatter(text)
    result.errors.extend(validate_skill_frontmatter(skill, meta))
    result.errors.extend(validate_skill_body(body))
    result.errors.extend(validate_markdown_links(skill_dir, text, known_skills))
    result.errors.extend(validate_rule_conversion(skill_file))
    return result


def validate_all_skills(repo_root: Path) -> dict[str, SkillValidationResult]:
    skills = install.discover_skills(repo_root)
    known = frozenset(skills)
    return {skill: validate_skill(skill, repo_root, known) for skill in skills}


def readme_skill_links(readme_text: str) -> dict[str, str]:
    """Map skill name to link target from README markdown tables."""
    links: dict[str, str] = {}
    for match in README_SKILL_LINK_RE.finditer(readme_text):
        links[match.group(1)] = match.group(2)
    return links


def validate_readme_skills(readme_path: Path, skills: list[str]) -> list[str]:
    if not readme_path.is_file():
        return [f"README not found: {readme_path}"]

    readme_text = readme_path.read_text(encoding="utf-8")
    links = readme_skill_links(readme_text)
    errors: list[str] = []

    for skill in skills:
        if skill not in links:
            errors.append(f"README missing table link for skill {skill!r}")
        elif links[skill] != skill:
            target = links[skill]
            errors.append(
                f"README link target for {skill!r} is {target!r}, expected {skill!r}"
            )

    extra = sorted(set(links) - set(skills))
    if extra:
        errors.append(f"README lists unknown skills: {', '.join(extra)}")

    return errors
