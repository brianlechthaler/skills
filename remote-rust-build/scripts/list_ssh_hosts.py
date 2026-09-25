#!/usr/bin/env python3
"""List concrete SSH Host entries that can be used as remote builders.

Reads an OpenSSH client config (default: ~/.ssh/config), including files
pulled in with Include. Prints only Host tokens that are real connectable
names. Wildcards and patterns (*, ?, [], and !negations) are skipped.
Hostnames are never invented: every printed name appears in the config.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_OK = 0
EXIT_MISSING = 2
EXIT_NONE = 3
MAX_INCLUDE_DEPTH = 8

_DIRECTIVE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*)(?:\s*=\s*|\s+)(.*)$")
_KEYWORD_ONLY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9]*)$")
_WILDCARD_CHARS = frozenset("*?[]")

MISSING_MSG = (
    "SSH config not found: {path}. "
    "No builder hosts to suggest. Ask the user for a builder host."
)
NOT_A_FILE_MSG = (
    "SSH config is not a file: {path}. "
    "No builder hosts to suggest. Ask the user for a builder host."
)
UNREADABLE_MSG = (
    "Cannot read SSH config {path}: {error}. "
    "No builder hosts to suggest. Ask the user for a builder host."
)
NO_HOSTS_MSG = (
    "SSH config {path} has no concrete Host entries "
    "(wildcards and patterns were skipped). "
    "No builder hosts to suggest. Ask the user for a builder host."
)


@dataclass(frozen=True)
class HostEntry:
    name: str
    hostname: str | None = None


def default_config_path() -> Path:
    return Path.home() / ".ssh" / "config"


def strip_inline_comment(line: str) -> str:
    in_single = False
    in_double = False
    result: list[str] = []
    for char in line:
        if char == "'" and not in_double:
            in_single = not in_single
            result.append(char)
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            result.append(char)
            continue
        if char == "#" and not in_single and not in_double:
            break
        result.append(char)
    return "".join(result)


def parse_directive(line: str) -> tuple[str, str] | None:
    raw = strip_inline_comment(line).strip()
    if not raw:
        return None
    match = _DIRECTIVE_RE.match(raw)
    if match:
        return match.group(1).lower(), match.group(2).strip()
    keyword = _KEYWORD_ONLY_RE.match(raw)
    if keyword:
        return keyword.group(1).lower(), ""
    return None


def unquote_token(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {'"', "'"}:
        return token[1:-1]
    return token


def is_concrete_host(token: str) -> bool:
    """True when token is a real Host alias, not a pattern or negation."""
    name = unquote_token(token)
    if not name or name.startswith("!"):
        return False
    if any(char in _WILDCARD_CHARS for char in name):
        return False
    return not any(char.isspace() for char in name)


def is_concrete_hostname(token: str) -> bool:
    if not is_concrete_host(token):
        return False
    return "%" not in unquote_token(token)


def _tokens(value: str) -> list[str]:
    return [unquote_token(token) for token in value.split() if token]


def _matching_files(pattern: Path) -> list[Path]:
    absolute = pattern.expanduser()
    if not absolute.is_absolute():
        absolute = Path.cwd() / absolute
    text = str(absolute)
    if not any(char in text for char in "*?["):
        return [absolute] if absolute.is_file() else []
    relative = absolute.relative_to(absolute.anchor)
    matches = Path(absolute.anchor).glob(str(relative))
    return sorted(path for path in matches if path.is_file())


def include_paths(value: str, include_base: Path) -> list[Path]:
    paths: list[Path] = []
    for token in value.split():
        token = unquote_token(token)
        if not token:
            continue
        expanded = Path(token).expanduser()
        if not expanded.is_absolute():
            expanded = include_base / expanded
        paths.extend(_matching_files(expanded))
    return paths


def _dedupe(entries: list[HostEntry]) -> list[HostEntry]:
    seen: set[str] = set()
    unique: list[HostEntry] = []
    for entry in entries:
        if entry.name in seen:
            continue
        seen.add(entry.name)
        unique.append(entry)
    return unique


def _parse(
    path: Path,
    include_base: Path,
    seen: set[Path],
    depth: int,
    *,
    required: bool,
) -> list[HostEntry]:
    if depth > MAX_INCLUDE_DEPTH:
        return []
    try:
        resolved = path.resolve()
    except OSError:
        if required:
            raise
        return []
    if resolved in seen:
        return []
    seen.add(resolved)
    try:
        text = resolved.read_text(encoding="utf-8", errors="replace")
    except OSError:
        if required:
            raise
        return []

    entries: list[HostEntry] = []
    pending: list[str] = []
    hostname: str | None = None

    def flush() -> None:
        nonlocal pending, hostname
        for name in pending:
            entries.append(HostEntry(name, hostname))
        pending = []
        hostname = None

    for line in text.splitlines():
        parsed = parse_directive(line)
        if parsed is None:
            continue
        key, value = parsed
        if key == "host":
            flush()
            pending = [token for token in _tokens(value) if is_concrete_host(token)]
        elif key == "match":
            flush()
        elif key == "include":
            flush()
            for included in include_paths(value, include_base):
                entries.extend(
                    _parse(
                        included,
                        include_base,
                        seen,
                        depth + 1,
                        required=False,
                    )
                )
        elif key == "hostname" and pending and hostname is None:
            tokens = _tokens(value)
            if tokens and is_concrete_hostname(tokens[0]):
                hostname = tokens[0]
    flush()
    return entries


def collect_hosts(path: Path) -> list[HostEntry]:
    """Return concrete Host entries from path, following Include directives."""
    config = path.expanduser()
    include_base = config.resolve().parent
    return _dedupe(_parse(config, include_base, set(), 0, required=True))


def format_host(entry: HostEntry) -> str:
    if entry.hostname and entry.hostname != entry.name:
        return f"{entry.name} hostname={entry.hostname}"
    return entry.name


def run(config_path: Path) -> int:
    path = config_path.expanduser()
    if not path.exists():
        print(MISSING_MSG.format(path=path), file=sys.stderr)
        return EXIT_MISSING
    if not path.is_file():
        print(NOT_A_FILE_MSG.format(path=path), file=sys.stderr)
        return EXIT_MISSING
    try:
        hosts = collect_hosts(path)
    except OSError as exc:
        print(UNREADABLE_MSG.format(path=path, error=exc), file=sys.stderr)
        return EXIT_MISSING
    if not hosts:
        print(NO_HOSTS_MSG.format(path=path), file=sys.stderr)
        return EXIT_NONE
    for entry in hosts:
        print(format_host(entry))
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="SSH config file (default: ~/.ssh/config)",
    )
    args = parser.parse_args(argv)
    config = args.config if args.config is not None else default_config_path()
    return run(config)


if __name__ == "__main__":
    raise SystemExit(main())
