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

## Skills (1)

| Skill | Description |
|-------|-------------|
| [docker](docker/SKILL.md) | Use Docker. |
"""


def test_expected_readme_text_updates_all_markers(sync_module) -> None:
    updated = sync_module.expected_readme_text(SAMPLE_README, 28)
    assert "<!-- skill-count:28 -->" in updated
    assert "— **28** reusable" in updated
    assert "## Skills (28)" in updated


def test_expected_readme_text_requires_markers(sync_module) -> None:
    with pytest.raises(ValueError, match="skill-count"):
        sync_module.expected_readme_text("# skills\n", 1)


def test_sync_readme_updates_when_out_of_sync(sync_module, tmp_path: Path, monkeypatch) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(SAMPLE_README, encoding="utf-8")

    repo_root = tmp_path
    for name in ("docker", "lint", "test"):
        skill_dir = repo_root / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# skill\n", encoding="utf-8")

    original_root = sync_module.ROOT
    sync_module.ROOT = repo_root
    monkeypatch.setattr(sync_module, "validate_skill_categories", lambda _discovered: None)
    try:
        assert sync_module.sync_readme(readme) == 0
        text = readme.read_text(encoding="utf-8")
        assert "<!-- skill-count:3 -->" in text
        assert "— **3** reusable" in text
        assert "## Skills (3)" in text
    finally:
        sync_module.ROOT = original_root


def test_sync_readme_check_fails_when_out_of_sync(sync_module, tmp_path: Path, monkeypatch) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(SAMPLE_README, encoding="utf-8")

    repo_root = tmp_path
    (repo_root / "docker").mkdir()
    (repo_root / "docker" / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (repo_root / "lint").mkdir()
    (repo_root / "lint" / "SKILL.md").write_text("# skill\n", encoding="utf-8")

    original_root = sync_module.ROOT
    sync_module.ROOT = repo_root
    monkeypatch.setattr(sync_module, "validate_skill_categories", lambda _discovered: None)
    try:
        assert sync_module.sync_readme(readme, check=True) == 1
        assert readme.read_text(encoding="utf-8") == SAMPLE_README
    finally:
        sync_module.ROOT = original_root
