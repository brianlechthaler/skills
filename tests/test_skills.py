"""Tests for skill_validate.py and every skill in the repository."""

from __future__ import annotations

from pathlib import Path

import pytest

import install
import skill_categories
import skill_validate

ROOT = Path(__file__).resolve().parent.parent
ALL_SKILLS = install.discover_skills(ROOT)


@pytest.fixture
def known_skills() -> frozenset[str]:
    return frozenset(ALL_SKILLS)


def test_every_repo_skill_is_discovered() -> None:
    assert len(ALL_SKILLS) == 49
    skill_categories.validate_skill_categories(ALL_SKILLS)


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_structure_and_content(skill: str, known_skills: frozenset[str]) -> None:
    """Each skill must have valid frontmatter, body, links, and rule conversion."""
    result = skill_validate.validate_skill(skill, ROOT, known_skills)
    assert result.ok, f"{skill} validation failed:\n  - " + "\n  - ".join(result.errors)


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_install_copy(skill: str, tmp_path: Path) -> None:
    """Each skill installs cleanly for Cursor via directory copy."""
    options = install.InstallOptions(
        repo_root=ROOT,
        project_dir=tmp_path / "project",
        home_dir=tmp_path / "home",
        method="copy",
    )
    options.project_dir.mkdir(parents=True)
    install.install_skill_for_agent(options, skill, "cursor")
    dest = options.project_dir / ".cursor/skills" / skill / "SKILL.md"
    assert dest.is_file()
    meta, body = install.parse_skill_frontmatter(dest.read_text(encoding="utf-8"))
    assert meta.get("name") == skill
    assert body.strip()


@pytest.mark.parametrize("skill", ALL_SKILLS)
def test_skill_rule_install_cursor(skill: str, tmp_path: Path) -> None:
    """Each skill converts to a Cursor rule file and installs under .cursor/rules."""
    options = install.InstallOptions(
        repo_root=ROOT,
        project_dir=tmp_path / "project",
        home_dir=tmp_path / "home",
    )
    options.project_dir.mkdir(parents=True)
    install.install_skill_as_rule_for_agent(options, skill, "cursor")
    rule = options.project_dir / ".cursor/rules" / f"{skill}.mdc"
    assert rule.is_file()
    text = rule.read_text(encoding="utf-8")
    assert "alwaysApply: false" in text
    assert "# " in text


def test_catalog_lists_every_skill() -> None:
    catalog = ROOT / "docs" / "features" / "skills-catalog.md"
    errors = skill_validate.validate_readme_skills(catalog, ALL_SKILLS)
    assert not errors, "\n".join(errors)


def test_strip_code_literals_removes_fenced_and_inline_code() -> None:
    text = "See `inline` and ```markdown\n[Link](missing.md)\n``` prose"
    stripped = skill_validate.strip_code_literals(text)
    assert "missing.md" not in stripped
    assert "inline" not in stripped
    assert "prose" in stripped


def test_validate_skill_frontmatter_detects_issues() -> None:
    errors = skill_validate.validate_skill_frontmatter(
        "docker",
        {"name": "wrong", "description": "too short"},
    )
    assert any("does not match directory" in err for err in errors)
    assert any("too short" in err for err in errors)


def test_validate_markdown_links_detects_broken_cross_skill(
    known_skills: frozenset[str],
) -> None:
    text = "Use [missing](../missing-skill/SKILL.md) when needed."
    errors = skill_validate.validate_markdown_links(
        ROOT / "docker",
        text,
        known_skills,
    )
    assert errors == ["broken cross-skill link: '../missing-skill/SKILL.md'"]


def test_validate_skill_reports_missing_file(tmp_path: Path) -> None:
    skill_dir = tmp_path / "sample"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("no frontmatter\n", encoding="utf-8")
    result = skill_validate.validate_skill("sample", tmp_path, frozenset({"sample"}))
    assert not result.ok
    assert any("missing YAML frontmatter" in err for err in result.errors)


def test_readme_skill_links_parses_table() -> None:
    readme = "| [docker](docker/SKILL.md) | desc |\n| [lint](lint/SKILL.md) | desc |"
    links = skill_validate.readme_skill_links(readme)
    assert links == {"docker": "docker", "lint": "lint"}


def test_validate_readme_skills_detects_missing() -> None:
    catalog = ROOT / "docs" / "features" / "skills-catalog.md"
    errors = skill_validate.validate_readme_skills(
        catalog,
        ["docker", "nonexistent-skill"],
    )
    assert any("missing table link" in err for err in errors)
