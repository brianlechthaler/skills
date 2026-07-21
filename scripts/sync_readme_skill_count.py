#!/usr/bin/env python3
"""Keep README and skills-catalog skill counts in sync with discoverable skills."""

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
SKILLS_CATALOG = ROOT / "docs" / "features" / "skills-catalog.md"
COUNT_MARKER = re.compile(r"<!-- skill-count:\d+ -->")
README_INTRO_COUNT = re.compile(r"— \*\*\d+\*\* reusable")
CATALOG_INTRO_COUNT = re.compile(r"All \*\*\d+\*\* portable")
SECTION_COUNT = re.compile(r"## Skills \(\d+\)")


def expected_readme_text(text: str, count: int) -> str:
    if not COUNT_MARKER.search(text):
        msg = "README.md is missing <!-- skill-count:N --> marker"
        raise ValueError(msg)
    if not README_INTRO_COUNT.search(text):
        msg = "README.md is missing intro skill count (— **N** reusable)"
        raise ValueError(msg)

    updated = COUNT_MARKER.sub(f"<!-- skill-count:{count} -->", text, count=1)
    return README_INTRO_COUNT.sub(f"— **{count}** reusable", updated, count=1)


def expected_catalog_text(text: str, count: int) -> str:
    if not COUNT_MARKER.search(text):
        msg = "skills-catalog.md is missing <!-- skill-count:N --> marker"
        raise ValueError(msg)
    if not CATALOG_INTRO_COUNT.search(text):
        msg = "skills-catalog.md is missing intro skill count (All **N** portable)"
        raise ValueError(msg)
    if not SECTION_COUNT.search(text):
        msg = "skills-catalog.md is missing ## Skills (N) heading"
        raise ValueError(msg)

    updated = COUNT_MARKER.sub(f"<!-- skill-count:{count} -->", text, count=1)
    updated = CATALOG_INTRO_COUNT.sub(f"All **{count}** portable", updated, count=1)
    return SECTION_COUNT.sub(f"## Skills ({count})", updated, count=1)


def _sync_file(
    path: Path,
    expected_fn,
    label: str,
    count: int,
    *,
    check: bool,
) -> int:
    text = path.read_text(encoding="utf-8")
    updated = expected_fn(text, count)

    if text == updated:
        print(f"{label} skill count already correct ({count})")
        return 0

    if check:
        print(
            f"{label} skill count is out of sync: expected {count}",
            file=sys.stderr,
        )
        return 1

    path.write_text(updated, encoding="utf-8")
    print(f"Updated {label} skill count to {count}")
    return 0


def sync_skill_counts(*, check: bool = False) -> int:
    discovered = discover_skills(ROOT)
    validate_skill_categories(discovered)
    count = len(discovered)

    readme_status = _sync_file(
        README, expected_readme_text, "README", count, check=check
    )
    catalog_status = _sync_file(
        SKILLS_CATALOG,
        expected_catalog_text,
        "skills-catalog.md",
        count,
        check=check,
    )
    return max(readme_status, catalog_status)


def sync_readme(readme: Path = README, *, check: bool = False) -> int:
    """Backward-compatible entry point; syncs README and skills catalog."""
    del readme
    return sync_skill_counts(check=check)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 when skill counts do not match discovered skills",
    )
    args = parser.parse_args()
    raise SystemExit(sync_skill_counts(check=args.check))


if __name__ == "__main__":
    main()
