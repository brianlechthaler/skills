"""High-level categories for skills in this repository."""

from __future__ import annotations

SKILL_CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "DevOps & CI",
        (
            "docker",
            "docker-optimize",
            "compose-deploy",
            "cloud-init",
            "github-workflows",
            "ci-optimize",
            "ci-debug",
            "dependabot-merge",
        ),
    ),
    (
        "GitHub",
        (
            "github-publish",
            "github-issues",
            "github-release",
            "github-merge-all",
        ),
    ),
    (
        "Documentation",
        (
            "document-project",
            "document-screenshots",
            "experimental-warning",
        ),
    ),
    (
        "Testing & Quality",
        (
            "test",
            "skill-test",
            "lint",
            "browser-test",
            "playwright-test",
            "skill-quality",
        ),
    ),
    (
        "Performance",
        (
            "web-performance",
            "compiled-performance",
            "interpreted-performance",
            "hardware-metrics",
            "valgrind-memcheck",
        ),
    ),
    (
        "Security",
        (
            "security-audit",
            "mcp-security",
            "prompt-security",
        ),
    ),
    (
        "MCP & Integrations",
        (
            "add-mcp-server",
            "codebase-memory",
            "headroom",
            "llm-backend-select",
            "llmfit",
            "slack-daily-plan",
            "gmail-daily-plan",
        ),
    ),
    (
        "Context & Efficiency",
        (
            "terse",
            "prompt-conciseness",
            "simple-code",
            "toonify",
        ),
    ),
    (
        "Orchestration",
        ("orchestrate",),
    ),
)


def category_for_skill(skill: str) -> str | None:
    for category, skills in SKILL_CATEGORIES:
        if skill in skills:
            return category
    return None


def validate_skill_categories(discovered: list[str]) -> None:
    """Ensure every discovered skill appears in exactly one category."""
    categorized = {skill for _, skills in SKILL_CATEGORIES for skill in skills}
    discovered_set = set(discovered)

    missing = sorted(discovered_set - categorized)
    if missing:
        msg = f"skills missing from SKILL_CATEGORIES: {', '.join(missing)}"
        raise ValueError(msg)

    extra = sorted(categorized - discovered_set)
    if extra:
        msg = f"SKILL_CATEGORIES lists unknown skills: {', '.join(extra)}"
        raise ValueError(msg)

    duplicates: list[str] = []
    seen: set[str] = set()
    for _, skills in SKILL_CATEGORIES:
        for skill in skills:
            if skill in seen:
                duplicates.append(skill)
            seen.add(skill)
    if duplicates:
        dupes = ", ".join(sorted(set(duplicates)))
        msg = f"skills listed in multiple categories: {dupes}"
        raise ValueError(msg)
