"""Tests for skill_categories.py."""

from __future__ import annotations

from pathlib import Path

import pytest

import install
import skill_categories


def test_all_repo_skills_are_categorized() -> None:
    root = Path(__file__).resolve().parent.parent
    discovered = install.discover_skills(root)
    skill_categories.validate_skill_categories(discovered)


def test_validate_skill_categories_detects_missing() -> None:
    with pytest.raises(ValueError, match="missing from SKILL_CATEGORIES"):
        skill_categories.validate_skill_categories(["docker", "unknown-skill"])


def test_validate_skill_categories_detects_extra() -> None:
    with pytest.raises(ValueError, match="lists unknown skills"):
        skill_categories.validate_skill_categories(["docker"])


def test_category_for_skill() -> None:
    assert skill_categories.category_for_skill("docker") == "Containers & Cloud"
    assert skill_categories.category_for_skill("missing") is None
