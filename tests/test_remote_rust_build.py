"""Tests for the remote-rust-build SSH host helper."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

import install
import skill_categories

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "remote-rust-build" / "scripts" / "list_ssh_hosts.py"


def _load():
    spec = importlib.util.spec_from_file_location("list_ssh_hosts", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


hosts = _load()


def test_skill_is_in_ci_category() -> None:
    assert "remote-rust-build" in install.discover_skills(ROOT)
    assert skill_categories.category_for_skill("remote-rust-build") == "CI/CD"


def test_copy_install_includes_host_helper(tmp_path: Path) -> None:
    options = install.InstallOptions(
        repo_root=ROOT,
        project_dir=tmp_path / "project",
        home_dir=tmp_path / "home",
        method="copy",
    )
    options.project_dir.mkdir(parents=True)
    install.install_skill_for_agent(options, "remote-rust-build", "cursor")
    script = (
        options.project_dir
        / ".cursor/skills/remote-rust-build/scripts/list_ssh_hosts.py"
    )
    assert script.is_file()
    assert not (ROOT / ".cursor").exists()
    assert not (ROOT / ".claude").exists()


def test_concrete_host_filters_patterns() -> None:
    assert hosts.is_concrete_host("builder")
    assert hosts.is_concrete_host('"quoted"')
    assert not hosts.is_concrete_host("*")
    assert not hosts.is_concrete_host("*.internal")
    assert not hosts.is_concrete_host("builder-?")
    assert not hosts.is_concrete_host("[abc]")
    assert not hosts.is_concrete_host("!skip")
    assert not hosts.is_concrete_host("")
    assert not hosts.is_concrete_hostname("box-%h")


def test_parse_directive_forms() -> None:
    assert hosts.parse_directive("  # comment") is None
    assert hosts.parse_directive("Host builder # note") == ("host", "builder")
    assert hosts.parse_directive("Host=equals-form") == ("host", "equals-form")
    assert hosts.parse_directive("Host = spaced") == ("host", "spaced")
    assert hosts.parse_directive("Host") == ("host", "")
    assert hosts.parse_directive("???") is None


def test_lists_concrete_hosts_and_skips_patterns(tmp_path: Path, capsys) -> None:
    included = tmp_path / "config.d"
    included.mkdir()
    (included / "lab.conf").write_text(
        "Host lab-box\n  HostName 10.1.2.3\n",
        encoding="utf-8",
    )
    config = tmp_path / "config"
    config.write_text(
        "\n".join(
            [
                "Host *",
                "  User dev",
                "Host *.internal builder-?",
                "  User dev",
                "Include config.d/*.conf",
                "Host builder extra",
                "  HostName build-01.example.com",
                "Host github.com",
                "  HostName github.com",
                "Host dup",
                "  HostName first.example",
                "Host dup",
                "  HostName second.example",
                "Match host *.example.com",
                "  User ubuntu",
                "Host quoted",
                "  HostName box-%h.example",
            ]
        ),
        encoding="utf-8",
    )
    assert hosts.run(config) == hosts.EXIT_OK
    output = capsys.readouterr().out.splitlines()
    assert output == [
        "lab-box hostname=10.1.2.3",
        "builder hostname=build-01.example.com",
        "extra hostname=build-01.example.com",
        "github.com",
        "dup hostname=first.example",
        "quoted",
    ]


def test_include_cycle_and_quoted_host(tmp_path: Path) -> None:
    first = tmp_path / "a"
    second = tmp_path / "b"
    first.write_text('Include b\nHost "from-a"\n', encoding="utf-8")
    second.write_text(
        "Include a\nHost from-b\n  HostName real.example\n",
        encoding="utf-8",
    )
    found = hosts.collect_hosts(first)
    assert [(entry.name, entry.hostname) for entry in found] == [
        ("from-b", "real.example"),
        ("from-a", None),
    ]


def test_tilde_include(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    extra = tmp_path / "extra.conf"
    extra.write_text("Host tilde-host\n", encoding="utf-8")
    config = tmp_path / "config"
    config.write_text("Include ~/extra.conf\n", encoding="utf-8")
    found = hosts.collect_hosts(config)
    assert [entry.name for entry in found] == ["tilde-host"]


def test_missing_config(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "no-such-config"
    assert hosts.run(missing) == hosts.EXIT_MISSING
    err = capsys.readouterr().err
    assert "SSH config not found" in err
    assert "Ask the user for a builder host" in err


def test_config_is_directory(tmp_path: Path, capsys) -> None:
    assert hosts.run(tmp_path) == hosts.EXIT_MISSING
    assert "not a file" in capsys.readouterr().err


def test_no_concrete_hosts(tmp_path: Path, capsys) -> None:
    config = tmp_path / "config"
    config.write_text("# Host commented\nHost *\nHost *.internal\n", encoding="utf-8")
    assert hosts.run(config) == hosts.EXIT_NONE
    err = capsys.readouterr().err
    assert "no concrete Host entries" in err
    assert "Ask the user for a builder host" in err


def test_unreadable_include_is_skipped(tmp_path: Path) -> None:
    config = tmp_path / "config"
    config.write_text("Include missing.conf\nHost kept\n", encoding="utf-8")
    assert [entry.name for entry in hosts.collect_hosts(config)] == ["kept"]


def test_unreadable_config(tmp_path: Path, capsys, monkeypatch) -> None:
    config = tmp_path / "config"
    config.write_text("Host kept\n", encoding="utf-8")

    def explode(path: Path) -> list[hosts.HostEntry]:
        del path
        raise OSError("permission denied")

    monkeypatch.setattr(hosts, "collect_hosts", explode)
    assert hosts.run(config) == hosts.EXIT_MISSING
    assert "Cannot read SSH config" in capsys.readouterr().err


def test_include_depth_limit(tmp_path: Path) -> None:
    current = tmp_path / "c0"
    current.write_text("Host depth-0\n", encoding="utf-8")
    for level in range(1, hosts.MAX_INCLUDE_DEPTH + 3):
        parent = tmp_path / f"c{level}"
        parent.write_text(
            f"Include c{level - 1}\nHost depth-{level}\n",
            encoding="utf-8",
        )
        current = parent
    found = {entry.name for entry in hosts.collect_hosts(current)}
    assert "depth-0" not in found
    assert f"depth-{hosts.MAX_INCLUDE_DEPTH}" in found


def test_main_uses_config_flag(tmp_path: Path, capsys) -> None:
    config = tmp_path / "config"
    config.write_text("Host from-main\n", encoding="utf-8")
    assert hosts.main(["--config", str(config)]) == 0
    assert capsys.readouterr().out.strip() == "from-main"


def test_main_default_path_missing(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(hosts, "default_config_path", lambda: tmp_path / "missing")
    assert hosts.main([]) == hosts.EXIT_MISSING
    assert "SSH config not found" in capsys.readouterr().err


def test_relative_glob_include(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "rel.conf").write_text("Host relative-host\n", encoding="utf-8")
    matches = hosts._matching_files(Path("rel.conf"))
    assert matches == [tmp_path / "rel.conf"]
    assert hosts._matching_files(Path("nope.conf")) == []


@pytest.mark.skipif(os.geteuid() == 0, reason="root can read mode 000 files")
def test_collect_hosts_permission_error(tmp_path: Path) -> None:
    config = tmp_path / "config"
    config.write_text("Host secret\n", encoding="utf-8")
    config.chmod(0)
    try:
        with pytest.raises(OSError):
            hosts.collect_hosts(config)
    finally:
        config.chmod(0o644)
