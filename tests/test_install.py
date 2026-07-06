"""Tests for install.py."""

from __future__ import annotations

import io
import os
import stat
import sys
import tarfile
from pathlib import Path
from unittest import mock

import pytest

import install

REQUIRED_COMPAT_AGENTS: tuple[str, ...] = (
    "claude-code",
    "codex",
    "gemini-cli",
    "openclaw",
    "hermes-agent",
    "mistral-vibe",
    "cursor",
    "aider",
    "windsurf",
    "kilo-code",
    "opencode",
    "augment",
    "antigravity",
)


@pytest.fixture
def repo_root(tmp_path: Path) -> Path:
    skill_dir = tmp_path / "docker"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: docker\ndescription: Use Docker\n---\n\n# Docker\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def options(repo_root: Path, tmp_path: Path) -> install.InstallOptions:
    return install.InstallOptions(
        repo_root=repo_root,
        project_dir=tmp_path / "project",
        home_dir=tmp_path / "home",
    )


def test_expand_home() -> None:
    home = Path("/home/user")
    assert install.expand_home("~/skills", home) == Path("/home/user/skills")
    assert install.expand_home("/abs/path", home) == Path("/abs/path")


def test_agent_and_rule_lookup() -> None:
    assert install.agent_by_id("cursor") is not None
    assert install.agent_by_id("missing") is None
    assert install.rule_by_id("cursor") is not None
    assert install.rule_by_id("missing") is None
    assert "cursor" in install.all_agent_ids()


def test_required_agent_compatibility() -> None:
    agent_ids = set(install.all_agent_ids())
    for agent_id in REQUIRED_COMPAT_AGENTS:
        assert agent_id in agent_ids, f"missing skill install mapping for {agent_id}"
        assert install.rule_by_id(agent_id) is not None, (
            f"missing rule install mapping for {agent_id}"
        )


@pytest.mark.parametrize(
    "agent_id,project_skill_path,global_skill_path",
    [
        ("openclaw", "skills", ".openclaw/skills"),
        ("hermes-agent", ".hermes/skills", ".hermes/skills"),
        ("mistral-vibe", ".vibe/skills", ".vibe/skills"),
        ("aider", ".aider/skills", ".aider/skills"),
        ("kilo-code", ".kilo/skills", ".kilo/skills"),
        ("augment", ".augment/skills", ".augment/skills"),
        ("antigravity", ".agents/skills", ".gemini/antigravity/skills"),
    ],
)
def test_new_agent_skill_paths(
    options: install.InstallOptions,
    agent_id: str,
    project_skill_path: str,
    global_skill_path: str,
) -> None:
    options.project_dir.mkdir(parents=True)
    assert (
        install.resolve_agent_dir(options, agent_id)
        == options.project_dir / project_skill_path
    )
    options.global_install = True
    assert (
        install.resolve_agent_dir(options, agent_id)
        == options.home_dir / global_skill_path
    )


def test_validate_skill_name_invalid() -> None:
    with pytest.raises(SystemExit):
        install.validate_skill_name("../evil")


def test_validate_agent_id_errors() -> None:
    with pytest.raises(SystemExit):
        install.validate_agent_id("missing", as_rule=False)
    with pytest.raises(SystemExit):
        install.validate_agent_id("missing", as_rule=True)
    install.validate_agent_id("all", as_rule=False)


def test_discover_skills(repo_root: Path, tmp_path: Path) -> None:
    assert install.discover_skills(repo_root) == ["docker"]
    assert install.discover_skills(tmp_path / "missing") == []
    hidden = tmp_path / ".hidden"
    hidden.mkdir()
    (hidden / "SKILL.md").write_text("x", encoding="utf-8")
    assert "hidden" not in install.discover_skills(tmp_path)


def test_list_skills_empty(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        install.list_skills(tmp_path)


def test_list_agents(capsys: pytest.CaptureFixture[str]) -> None:
    install.list_agents()
    output = capsys.readouterr().out
    assert "cursor" in output
    assert "openclaw" in output
    assert "hermes-agent" in output
    assert "mistral-vibe" in output
    assert "RULE PROJECT" in output


def test_resolve_agent_dir(options: install.InstallOptions) -> None:
    options.project_dir.mkdir()
    assert (
        install.resolve_agent_dir(options, "cursor")
        == options.project_dir / ".cursor/skills"
    )
    options.global_install = True
    assert (
        install.resolve_agent_dir(options, "cursor")
        == options.home_dir / ".cursor/skills"
    )
    with pytest.raises(SystemExit):
        install.resolve_agent_dir(options, "missing")


def test_resolve_rule_target(options: install.InstallOptions) -> None:
    options.project_dir.mkdir()
    target, delivery, fmt = install.resolve_rule_target(options, "cursor")
    assert target == options.project_dir / ".cursor/rules"
    assert delivery == "per-file"
    assert fmt == "cursor"

    target, delivery, fmt = install.resolve_rule_target(options, "opencode")
    assert delivery == "append"
    assert fmt == "plain"

    target, delivery, fmt = install.resolve_rule_target(options, "windsurf")
    assert target == options.project_dir / ".windsurf/rules"

    options.global_install = True
    target, delivery, fmt = install.resolve_rule_target(options, "windsurf")
    assert target == options.home_dir / ".codeium/windsurf/memories/global_rules.md"
    assert delivery == "append"

    target, delivery, fmt = install.resolve_rule_target(options, "github-copilot")
    assert delivery == "append"
    assert target == options.home_dir / ".copilot/copilot-instructions.md"

    target, delivery, fmt = install.resolve_rule_target(options, "cline")
    assert delivery == "per-file"


def test_rule_filename_for_skill() -> None:
    assert install.rule_filename_for_skill("test", "cursor") == "test.mdc"
    assert install.rule_filename_for_skill("test", "plain") == "test.md"


def test_parse_skill_frontmatter_variants() -> None:
    meta, body = install.parse_skill_frontmatter("no frontmatter")
    assert meta == {}
    assert body == "no frontmatter"

    text = "---\nname: foo\ndescription: >-\n  line one\n  line two\n---\n\nBody\n"
    meta, body = install.parse_skill_frontmatter(text)
    assert meta["name"] == "foo"
    assert "line one line two" in meta["description"]
    assert body.startswith("\nBody")

    text = "---\nname: bar\ndescription: inline desc\n---\n\nMore\n"
    meta, body = install.parse_skill_frontmatter(text)
    assert meta["description"] == "inline desc"


def test_convert_skill_to_rule_formats(repo_root: Path) -> None:
    skill_file = repo_root / "docker" / "SKILL.md"
    assert "alwaysApply: false" in install.convert_skill_to_rule(skill_file, "cursor")
    assert install.convert_skill_to_rule(skill_file, "claude").startswith("---")
    assert "trigger: model_decision" in install.convert_skill_to_rule(
        skill_file, "windsurf"
    )
    plain = install.convert_skill_to_rule(skill_file, "plain")
    assert "# Docker" in plain
    assert "> Use Docker" in plain

    plain_skill = repo_root / "plain-skill"
    plain_skill.mkdir()
    (plain_skill / "SKILL.md").write_text(
        "---\nname: plain-skill\n---\n\nOnly body\n", encoding="utf-8"
    )
    plain_only = install.convert_skill_to_rule(plain_skill / "SKILL.md", "plain")
    assert "Only body" in plain_only


def test_upsert_marked_section(tmp_path: Path) -> None:
    target = tmp_path / "AGENTS.md"
    install.upsert_marked_section(target, "docker", "content one")
    assert "<!-- skills-install:docker:begin -->" in target.read_text(encoding="utf-8")

    install.upsert_marked_section(target, "docker", "content two")
    text = target.read_text(encoding="utf-8")
    assert "content two" in text
    assert "content one" not in text


def test_command_on_path() -> None:
    assert isinstance(install.command_on_path("python3"), bool)


def test_detect_agents(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    (home / ".cursor").mkdir()
    assert "cursor" in install.detect_agents(home)

    empty_home = tmp_path / "empty"
    empty_home.mkdir()
    assert install.detect_agents(empty_home) == ["cursor", "claude-code", "opencode"]


def test_detect_agents_via_command(tmp_path: Path) -> None:
    home = tmp_path / "home2"
    home.mkdir()
    with mock.patch("install.shutil.which", return_value="/usr/bin/claude"):
        detected = install.detect_agents(home)
    assert "claude-code" in detected


def test_detect_new_agents(tmp_path: Path) -> None:
    home = tmp_path / "home3"
    home.mkdir()
    (home / ".openclaw").mkdir()
    (home / ".hermes").mkdir()
    (home / ".vibe").mkdir()
    (home / ".augment").mkdir()
    detected = install.detect_agents(home)
    assert "openclaw" in detected
    assert "hermes-agent" in detected
    assert "mistral-vibe" in detected
    assert "augment" in detected


def test_expand_agents() -> None:
    expanded = install.expand_agents(["all"], as_rule=False)
    assert expanded == install.all_agent_ids()
    assert install.expand_agents(["cursor"], as_rule=False) == ["cursor"]
    with pytest.raises(SystemExit):
        install.expand_agents(["bad"], as_rule=False)


def test_expand_skills(options: install.InstallOptions) -> None:
    assert install.expand_skills(options) == ["docker"]
    options.install_all_skills = True
    assert install.expand_skills(options) == ["docker"]
    options.install_all_skills = False
    options.skills = ["docker"]
    assert install.expand_skills(options) == ["docker"]
    options.skills = ["missing"]
    with pytest.raises(SystemExit):
        install.expand_skills(options)


def test_validate_tarball_url() -> None:
    install.validate_tarball_url("https://github.com/org/repo/archive/main.tar.gz")
    with pytest.raises(SystemExit):
        install.validate_tarball_url("http://github.com/x.tar.gz")
    with pytest.raises(SystemExit):
        install.validate_tarball_url("https://evil.com/x.tar.gz")


def test_safe_extract_tar_blocks_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "bad.tar"
    dest = tmp_path / "dest"
    dest.mkdir()
    with tarfile.open(archive, "w") as tar:
        info = tarfile.TarInfo(name="../escape.txt")
        info.size = 4
        tar.addfile(info, io.BytesIO(b"evil"))

    with tarfile.open(archive, "r") as tar:
        with pytest.raises(SystemExit):
            install.safe_extract_tar(tar, dest)


def test_safe_extract_tar_ok(tmp_path: Path) -> None:
    archive = tmp_path / "ok.tar"
    dest = tmp_path / "dest2"
    dest.mkdir()
    payload = tmp_path / "payload.txt"
    payload.write_text("ok", encoding="utf-8")
    with tarfile.open(archive, "w") as tar:
        tar.add(payload, arcname="payload.txt")

    with tarfile.open(archive, "r") as tar:
        install.safe_extract_tar(tar, dest)
    assert (dest / "payload.txt").read_text(encoding="utf-8") == "ok"


def test_fetch_repo_if_needed_local(options: install.InstallOptions) -> None:
    install.fetch_repo_if_needed(options)
    assert options.tmp_repo is None


def test_fetch_repo_if_needed_remote(tmp_path: Path) -> None:
    options = install.InstallOptions(
        repo_root=tmp_path / "empty", home_dir=tmp_path / "home"
    )
    (tmp_path / "empty").mkdir()

    archive_bytes = io.BytesIO()
    with tarfile.open(fileobj=archive_bytes, mode="w:gz") as tar:
        skill_dir = tmp_path / "build" / "remote-skill"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(
            "---\nname: remote-skill\n---\n\nBody\n", encoding="utf-8"
        )
        tar.add(skill_dir, arcname="skills-main/remote-skill")

    class FakeResponse:
        def read(self) -> bytes:
            archive_bytes.seek(0)
            return archive_bytes.read()

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    with mock.patch("install.urlopen", return_value=FakeResponse()):
        install.fetch_repo_if_needed(options)

    assert "remote-skill" in install.discover_skills(options.repo_root)
    install.cleanup(options)


def test_fetch_repo_invalid_env(tmp_path: Path) -> None:
    options = install.InstallOptions(repo_root=tmp_path / "empty")
    (tmp_path / "empty").mkdir()
    with mock.patch.dict(os.environ, {"SKILLS_GITHUB_REPO": "../bad"}):
        with pytest.raises(SystemExit):
            install.fetch_repo_if_needed(options)


def test_fetch_repo_network_error(tmp_path: Path) -> None:
    options = install.InstallOptions(repo_root=tmp_path / "empty")
    (tmp_path / "empty").mkdir()
    with mock.patch("install.urlopen", side_effect=OSError("network down")):
        with pytest.raises(SystemExit):
            install.fetch_repo_if_needed(options)


def test_cleanup(options: install.InstallOptions, tmp_path: Path) -> None:
    options.tmp_repo = tmp_path / "tmp"
    options.tmp_repo.mkdir()
    install.cleanup(options)
    assert options.tmp_repo is None


def test_make_executable_sh_files(
    options: install.InstallOptions, tmp_path: Path
) -> None:
    dest = tmp_path / "skill"
    dest.mkdir()
    sh_file = dest / "run.sh"
    sh_file.write_text("#!/bin/sh\n", encoding="utf-8")
    with mock.patch("install.os.name", "posix"):
        install.make_executable_sh_files(dest)
    assert sh_file.stat().st_mode & stat.S_IXUSR

    with mock.patch("install.os.name", "nt"):
        install.make_executable_sh_files(dest)


def test_remove_destination_variants(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    install.remove_destination(missing)

    link = tmp_path / "link"
    target = tmp_path / "target.txt"
    target.write_text("x", encoding="utf-8")
    link.symlink_to(target)
    install.remove_destination(link)
    assert not link.exists()

    directory = tmp_path / "dir"
    directory.mkdir()
    install.remove_destination(directory)
    assert not directory.exists()

    plain = tmp_path / "file.txt"
    plain.write_text("x", encoding="utf-8")
    install.remove_destination(plain)
    assert not plain.exists()


def test_install_skill_copy(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    options.method = "copy"
    install.install_skill_for_agent(options, "docker", "cursor")
    dest = options.project_dir / ".cursor/skills/docker/SKILL.md"
    assert dest.is_file()


def test_install_skill_symlink(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    options.method = "symlink"
    install.install_skill_for_agent(options, "docker", "cursor")
    dest = options.project_dir / ".cursor/skills/docker"
    assert dest.is_symlink() or dest.is_dir()


def test_install_skill_symlink_fallback(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    options.method = "symlink"
    with mock.patch("install.Path.symlink_to", side_effect=OSError("nope")):
        install.install_skill_for_agent(options, "docker", "cursor")
    dest = options.project_dir / ".cursor/skills/docker/SKILL.md"
    assert dest.is_file()


def test_install_skill_missing(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    with pytest.raises(SystemExit):
        install.install_skill_for_agent(options, "missing", "cursor")


def test_install_rule_per_file(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    install.install_skill_as_rule_for_agent(options, "docker", "cursor")
    rule = options.project_dir / ".cursor/rules/docker.mdc"
    assert rule.is_file()


def test_install_rule_append(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    install.install_skill_as_rule_for_agent(options, "docker", "opencode")
    agents_md = options.project_dir / "AGENTS.md"
    assert "skills-install:docker" in agents_md.read_text(encoding="utf-8")


def test_install_rule_append_aider(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    install.install_skill_as_rule_for_agent(options, "docker", "aider")
    conventions = options.project_dir / "CONVENTIONS.md"
    assert "skills-install:docker" in conventions.read_text(encoding="utf-8")


def test_install_skill_openclaw(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    options.method = "copy"
    install.install_skill_for_agent(options, "docker", "openclaw")
    dest = options.project_dir / "skills/docker/SKILL.md"
    assert dest.is_file()


def test_confirm() -> None:
    assert install.confirm("Proceed?", yes=True)
    with mock.patch("builtins.input", return_value="y"):
        assert install.confirm("Proceed?", yes=False)
    with mock.patch("builtins.input", return_value="n"):
        assert not install.confirm("Proceed?", yes=False)


def test_run_install_cancelled(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    options.agents = ["cursor"]
    options.yes = False
    with mock.patch("builtins.input", return_value="n"):
        assert install.run_install(options) == 0


def test_run_install_success(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    options.agents = ["cursor"]
    options.yes = True
    assert install.run_install(options) == 0


def test_run_install_as_rule(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    options.as_rule = True
    options.agents = ["cursor"]
    options.yes = True
    assert install.run_install(options) == 0


def test_main_list_agents() -> None:
    assert install.main(["--list-agents"]) == 0


def test_main_list(repo_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SKILLS_REPO_ROOT", str(repo_root))
    assert install.main(["--list"]) == 0


def test_main_install(
    repo_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SKILLS_REPO_ROOT", str(repo_root))
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    assert install.main(["-s", "docker", "-a", "cursor", "-y"]) == 0


def test_resolve_rule_target_missing(options: install.InstallOptions) -> None:
    with pytest.raises(SystemExit):
        install.resolve_rule_target(options, "missing")


def test_upsert_without_trailing_newline(tmp_path: Path) -> None:
    target = tmp_path / "AGENTS.md"
    target.write_text("prefix", encoding="utf-8")
    install.upsert_marked_section(target, "docker", "content")
    assert target.read_text(encoding="utf-8").startswith("prefix\n")


def test_safe_extract_tar_legacy_python(tmp_path: Path) -> None:
    archive = tmp_path / "legacy.tar"
    dest = tmp_path / "dest3"
    dest.mkdir()
    payload = tmp_path / "payload2.txt"
    payload.write_text("ok", encoding="utf-8")
    with tarfile.open(archive, "w") as tar:
        tar.add(payload, arcname="payload2.txt")

    with tarfile.open(archive, "r") as tar:
        with mock.patch.object(install.sys, "version_info", (3, 10, 0)):
            install.safe_extract_tar(tar, dest)
    assert (dest / "payload2.txt").is_file()


def test_fetch_repo_invalid_branch(tmp_path: Path) -> None:
    options = install.InstallOptions(repo_root=tmp_path / "empty")
    (tmp_path / "empty").mkdir()
    with mock.patch.dict(os.environ, {"SKILLS_GITHUB_BRANCH": "../bad"}):
        with pytest.raises(SystemExit):
            install.fetch_repo_if_needed(options)


def test_fetch_repo_switches_to_copy(tmp_path: Path) -> None:
    options = install.InstallOptions(
        repo_root=tmp_path / "empty",
        home_dir=tmp_path / "home",
        method="symlink",
    )
    (tmp_path / "empty").mkdir()

    archive_bytes = io.BytesIO()
    with tarfile.open(fileobj=archive_bytes, mode="w:gz") as tar:
        skill_dir = tmp_path / "build2" / "remote-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: remote-skill\n---\n\nBody\n", encoding="utf-8"
        )
        tar.add(skill_dir, arcname="skills-main/remote-skill")

    class FakeResponse:
        def read(self) -> bytes:
            archive_bytes.seek(0)
            return archive_bytes.read()

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    with mock.patch("install.urlopen", return_value=FakeResponse()):
        install.fetch_repo_if_needed(options)

    assert options.method == "copy"
    install.cleanup(options)


def test_fetch_repo_tar_error(tmp_path: Path) -> None:
    options = install.InstallOptions(repo_root=tmp_path / "empty")
    (tmp_path / "empty").mkdir()

    class FakeResponse:
        def read(self) -> bytes:
            return b"not-a-tarball"

        def __enter__(self) -> FakeResponse:
            return self

        def __exit__(self, *args: object) -> None:
            return None

    with mock.patch("install.urlopen", return_value=FakeResponse()):
        with pytest.raises(SystemExit):
            install.fetch_repo_if_needed(options)


def test_install_rule_missing(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    with pytest.raises(SystemExit):
        install.install_skill_as_rule_for_agent(options, "missing", "cursor")


def test_run_install_auto_detect(options: install.InstallOptions) -> None:
    options.project_dir.mkdir(parents=True)
    options.agents = []
    options.yes = True
    (options.home_dir / ".cursor").mkdir(parents=True)
    assert install.run_install(options) == 0


def test_main_missing_repo_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SKILLS_REPO_ROOT", str(tmp_path / "missing"))
    with pytest.raises(SystemExit):
        install.main(["--list"])


def test_main_missing_repo_on_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SKILLS_REPO_ROOT", str(tmp_path / "missing"))
    with pytest.raises(SystemExit):
        install.main(["-y"])


def test_build_parser() -> None:
    parser = install.build_parser()
    args = parser.parse_args(["--all", "-a", "cursor", "docker"])
    assert args.install_all
    assert args.agents == ["cursor"]
    assert args.positional_skills == ["docker"]


def test_err_and_info(capsys: pytest.CaptureFixture[str]) -> None:
    install.info("hello")
    install.ok("done")
    captured = capsys.readouterr()
    assert "hello" in captured.out
    assert "done" in captured.out
    with pytest.raises(SystemExit) as exc:
        install.err("boom")
    assert exc.value.code == 1


def test_main_entrypoint() -> None:
    with mock.patch("install.main", return_value=0):
        with mock.patch.object(sys, "argv", ["install.py", "--list-agents"]):
            with pytest.raises(SystemExit) as exc:
                import runpy

                runpy.run_path(
                    str(Path(__file__).resolve().parents[1] / "install.py"),
                    run_name="__main__",
                )
    assert exc.value.code == 0
