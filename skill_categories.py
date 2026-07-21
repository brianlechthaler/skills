"""High-level categories for skills in this repository."""

from __future__ import annotations

SKILL_CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Containers & Cloud",
        (
            "cloud-init",
            "compose-deploy",
            "docker",
            "docker-optimize",
        ),
    ),
    (
        "CI/CD",
        (
            "ci-debug",
            "ci-optimize",
            "dependabot-merge",
            "github-workflows",
        ),
    ),
    (
        "GitHub",
        (
            "github-issues",
            "github-merge-all",
            "github-prune-branches",
            "github-publish",
            "github-release",
        ),
    ),
    (
        "Documentation",
        (
            "document-project",
            "document-screenshots",
            "experimental-warning",
            "hardware-requirements",
        ),
    ),
    (
        "Testing",
        (
            "browser-test",
            "lint",
            "playwright-test",
            "test",
        ),
    ),
    (
        "Agent Skills",
        (
            "skill-create",
            "skill-quality",
            "skill-test",
        ),
    ),
    (
        "Performance & Observability",
        (
            "compiled-performance",
            "hardware-metrics",
            "interpreted-performance",
            "opentelemetry",
            "valgrind-memcheck",
            "web-performance",
        ),
    ),
    (
        "Security",
        (
            "mcp-security",
            "prompt-security",
            "security-audit",
        ),
    ),
    (
        "MCP",
        (
            "add-mcp-server",
            "codebase-memory",
            "headroom",
        ),
    ),
    (
        "Local LLM",
        (
            "llm-backend-select",
            "llmfit",
        ),
    ),
    (
        "Productivity & Planning",
        (
            "daily-plan",
            "gmail-daily-plan",
            "jira-daily-plan",
            "slack-daily-plan",
        ),
    ),
    (
        "Context & Efficiency",
        (
            "caveman",
            "prompt-conciseness",
            "simple-code",
            "terse",
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
