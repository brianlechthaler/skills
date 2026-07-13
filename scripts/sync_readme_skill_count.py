#!/usr/bin/env python3
"""Keep README.md skill counts in sync with discoverable skills."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from install import discover_skills  # noqa: E402
from skill_categories import validate_skill_categories  # noqa: E402

README = ROOT / "README.md"
COUNT_MARKER = re.compile(r"<!-- skill-count:\d+ -->")
INTRO_COUNT = re.compile(r"— \*\*\d+\*\* reusable")
SECTION_COUNT = re.compile(r"## Skills \(\d+\)")


def expected_readme_text(text: str, count: int) -> str:
    if not COUNT_MARKER.search(text):
        msg = "README.md is missing <!-- skill-count:N --> marker"
        raise ValueError(msg)
    if not INTRO_COUNT.search(text):
        msg = "README.md is missing intro skill count (— **N** reusable)"
        raise ValueError(msg)
    if not SECTION_COUNT.search(text):
        msg = "README.md is missing ## Skills (N) heading"
        raise ValueError(msg)

    updated = COUNT_MARKER.sub(f"<!-- skill-count:{count} -->", text, count=1)
    updated = INTRO_COUNT.sub(f"— **{count}** reusable", updated, count=1)
    updated = SECTION_COUNT.sub(f"## Skills ({count})", updated, count=1)
    return updated


def sync_readme(readme: Path = README, *, check: bool = False) -> int:
    discovered = discover_skills(ROOT)
    validate_skill_categories(discovered)
    count = len(discovered)
    text = readme.read_text(encoding="utf-8")
    updated = expected_readme_text(text, count)

    if text == updated:
        print(f"README skill count already correct ({count})")
        return 0

    if check:
        print(
            f"README skill count is out of sync: expected {count}",
            file=sys.stderr,
        )
        return 1

    readme.write_text(updated, encoding="utf-8")
    print(f"Updated README skill count to {count}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 when README count does not match discovered skills",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=README,
        help="README path (default: repo README.md)",
    )
    args = parser.parse_args()
    raise SystemExit(sync_readme(args.readme, check=args.check))


if __name__ == "__main__":
    main()
