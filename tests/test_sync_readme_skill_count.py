"""Tests for scripts/sync_readme_skill_count.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "sync_readme_skill_count.py"


def load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_readme_skill_count", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["sync_readme_skill_count"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def sync_module():
    return load_sync_module()


SAMPLE_README = """\
# skills

<!-- skill-count:1 -->
Intro — **1** reusable instructions.
"""

SAMPLE_CATALOG = """\
# Skills catalog

<!-- skill-count:1 -->
All **1** portable skills.

## Skills (1)

| Skill | Description |
|-------|-------------|
| [docker](../../docker/SKILL.md) | Use Docker. |
"""


def test_expected_readme_text_updates_markers(sync_module) -> None:
    updated = sync_module.expected_readme_text(SAMPLE_README, 28)
    assert "<!-- skill-count:28 -->" in updated
    assert "— **28** reusable" in updated


def test_expected_catalog_text_updates_all_markers(sync_module) -> None:
    updated = sync_module.expected_catalog_text(SAMPLE_CATALOG, 28)
    assert "<!-- skill-count:28 -->" in updated
    assert "All **28** portable" in updated
    assert "## Skills (28)" in updated


def test_expected_readme_text_requires_markers(sync_module) -> None:
    with pytest.raises(ValueError, match="skill-count"):
        sync_module.expected_readme_text("# skills\n", 1)


def test_sync_skill_counts_updates_when_out_of_sync(
    sync_module, tmp_path: Path, monkeypatch
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(SAMPLE_README, encoding="utf-8")
    catalog = tmp_path / "skills-catalog.md"
    catalog.write_text(SAMPLE_CATALOG, encoding="utf-8")

    repo_root = tmp_path
    for name in ("docker", "lint", "test"):
        skill_dir = repo_root / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# skill\n", encoding="utf-8")

    original_root = sync_module.ROOT
    sync_module.ROOT = repo_root
    sync_module.README = readme
    sync_module.SKILLS_CATALOG = catalog
    monkeypatch.setattr(
        sync_module, "validate_skill_categories", lambda _discovered: None
    )
    try:
        assert sync_module.sync_skill_counts() == 0
        assert "<!-- skill-count:3 -->" in readme.read_text(encoding="utf-8")
        assert "— **3** reusable" in readme.read_text(encoding="utf-8")
        catalog_text = catalog.read_text(encoding="utf-8")
        assert "<!-- skill-count:3 -->" in catalog_text
        assert "All **3** portable" in catalog_text
        assert "## Skills (3)" in catalog_text
    finally:
        sync_module.ROOT = original_root
        sync_module.README = original_root / "README.md"
        sync_module.SKILLS_CATALOG = (
            original_root / "docs" / "features" / "skills-catalog.md"
        )


def test_sync_skill_counts_check_fails_when_out_of_sync(
    sync_module, tmp_path: Path, monkeypatch
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(SAMPLE_README, encoding="utf-8")
    catalog = tmp_path / "skills-catalog.md"
    catalog.write_text(SAMPLE_CATALOG, encoding="utf-8")

    repo_root = tmp_path
    (repo_root / "docker").mkdir()
    (repo_root / "docker" / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (repo_root / "lint").mkdir()
    (repo_root / "lint" / "SKILL.md").write_text("# skill\n", encoding="utf-8")

    original_root = sync_module.ROOT
    sync_module.ROOT = repo_root
    sync_module.README = readme
    sync_module.SKILLS_CATALOG = catalog
    monkeypatch.setattr(
        sync_module, "validate_skill_categories", lambda _discovered: None
    )
    try:
        assert sync_module.sync_skill_counts(check=True) == 1
        assert readme.read_text(encoding="utf-8") == SAMPLE_README
        assert catalog.read_text(encoding="utf-8") == SAMPLE_CATALOG
    finally:
        sync_module.ROOT = original_root
        sync_module.README = original_root / "README.md"
        sync_module.SKILLS_CATALOG = (
            original_root / "docs" / "features" / "skills-catalog.md"
        )
