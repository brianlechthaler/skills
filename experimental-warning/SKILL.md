---
name: experimental-warning
description: >-
  Add visible experimental, alpha, beta, or preview warning banners across all
  user-facing surfaces — web UI, CLI, TUI, desktop, mobile, and API docs. Use
  when shipping pre-release software, marking features experimental, or when the
  user asks for warning banners, disclaimers, or pre-release notices.
---

# Experimental Warning

Ship **clear, consistent pre-release warnings** on every surface users touch. The warning must be impossible to miss on first use and remain visible during normal operation.

## Core Requirements

When software or a feature is experimental, alpha, beta, or preview:

- **Show a warning on every UX surface** — web UI, CLI, TUI, desktop shell, mobile app, installer, and public API docs
- **Use one canonical message** per release stage across all surfaces (same meaning; format may adapt to the medium)
- **Make it visible before work begins** — banner on first screen, stderr notice before prompts, startup splash, or equivalent
- **Do not rely on color alone** — include text and an icon or label; meet contrast and screen-reader requirements
- **State consequences plainly** — data loss, breaking changes, missing support, and no production-use guarantee
- **Link to feedback or docs** when a URL exists (issue tracker, changelog, stability policy)

These are hard gates for pre-release UX. Do not mark the work complete until each applicable surface shows the warning in a real run.

For overall documentation of stability tiers, see [document-project](../document-project/SKILL.md). For web UI verification after adding banners, use [browser-test](../browser-test/SKILL.md).

## When This Applies

| Applies | Does not apply |
|---------|----------------|
| New projects marked experimental, alpha, beta, or preview | Stable GA releases with no pre-release qualifier |
| Individual features flagged experimental behind a flag | Internal-only tools with no external users |
| CLI, TUI, web, desktop, or mobile user interfaces | Pure libraries with no runnable entry point |
| Public HTTP APIs or SDKs in pre-release | User explicitly says "no warning banner" |
| User asks for disclaimer, preview notice, or pre-release warning | Removing warnings when promoting to stable GA |

When unsure and the product is not production-ready, default to **show the warning**.

## Release-Stage Vocabulary

Pick **one** stage label per scope and use it consistently:

| Stage | Meaning | Typical banner tone |
|-------|---------|---------------------|
| **Experimental** | May change or disappear without notice; APIs and behavior unstable | Strongest caution; discourage production use |
| **Alpha** | Early testing; incomplete; frequent breaking changes | Strong caution; invite feedback |
| **Beta** | Feature-complete enough to test; breaking changes less frequent | Moderate caution; not recommended for production |
| **Preview** | Near-stable preview of an upcoming capability | Lighter caution; may still change |

Do not mix stage names on the same surface (e.g. "beta experimental"). If the repo already defines stages, match existing terminology.

## Canonical Copy Template

Adapt bracketed parts; keep the same facts everywhere:

```
[STAGE]: This software is pre-release. It may break, lose data, or change without notice.
Not recommended for production use. [Optional: Report issues at URL.]
```

Short CLI one-liner variant:

```
warning: [PROJECT] is [STAGE] — not recommended for production; behavior may change without notice.
```

## Workflow

Copy and track:

```
Experimental warning progress:
- [ ] Release stage chosen (experimental / alpha / beta / preview)
- [ ] Canonical copy written (one message for all surfaces)
- [ ] Web UI banner added (if applicable)
- [ ] CLI / TUI startup warning added (if applicable)
- [ ] Desktop / mobile shell warning added (if applicable)
- [ ] API / SDK / OpenAPI stability notice added (if applicable)
- [ ] Docs and README stability section updated
- [ ] Accessibility and contrast checked
- [ ] Verified in a real run on each surface
```

### Step 1 — Inventory surfaces

List every way users encounter the software:

| Surface | Where to warn | Notes |
|---------|---------------|-------|
| Web app | Top of layout, above nav; persist on all routes | Sticky or repeated in root layout |
| CLI | stderr on startup; repeat in `help` / `--version` | Respect `--quiet` only if documented |
| TUI | Header bar or first screen panel | Do not flash once and hide |
| Desktop (Electron, etc.) | Title bar badge, top banner, or about dialog on first launch | Banner beats about-only |
| Mobile | Top banner or first-run modal plus persistent settings label | Follow platform HIG where possible |
| HTTP API | `Sunset` / custom header, OpenAPI `info.description`, response `Warning` field optional | Docs must match runtime |
| Installer / onboarding | First screen before account or data entry | Same copy as runtime |

Skip only surfaces that truly do not exist for the project.

### Step 2 — Implement per surface

**Web UI** — persistent top banner in the root layout:

```html
<div role="status" aria-live="polite" class="experimental-banner">
  <strong>Experimental.</strong>
  This software is pre-release. It may break, lose data, or change without notice.
  Not recommended for production use.
</div>
```

- Place above primary navigation and main content
- Use warning palette with sufficient contrast (WCAG AA minimum)
- Do not hide behind a one-time dismiss unless product policy requires it; if dismissible, show again on next session

**CLI** — print to stderr before interactive work:

```python
import sys

WARNING = (
    "warning: myapp is experimental — not recommended for production; "
    "behavior may change without notice.\n"
)

def warn_if_experimental() -> None:
    if not os.environ.get("MYAPP_QUIET"):
        print(WARNING, file=sys.stderr)
```

- Call from `main()` before subcommands run
- Include the stage in `--help` description and README
- Optional `MYAPP_EXPERIMENTAL=0` only for CI harnesses — never default off for real users

**TUI** — dedicated header row or styled panel visible on every screen; reuse the canonical sentence.

**API / OpenAPI** — prefix `info.description`:

```yaml
info:
  title: My API
  description: |
    **Experimental.** This API is unstable and may change without notice.
    Not recommended for production use.
```

### Step 3 — Document and cross-link

Add a short **Stability** section to README and `docs/` pointing to the same stage definitions. Mention how to report bugs. Keep wording aligned with in-app banners — no softer language in docs.

### Step 4 — Verify

On each surface:

1. Cold start — warning appears before the user can take destructive action
2. Screen reader or `aria-live` announces web banner
3. `myapp --help` and `myapp --version` mention the stage (CLI)
4. Banner survives navigation (web) and subcommands (CLI)
5. No surface contradicts another on stage name or severity

Use [browser-test](../browser-test/SKILL.md) for web flows; run the CLI/TUI binary directly for terminal surfaces.

## Checklist

Full review list: [checklist.md](checklist.md)

## Anti-Patterns

| Avoid | Do instead |
|-------|------------|
| Warning only in README | Runtime banner on every UX surface |
| Tiny gray text users overlook | High-contrast banner with bold stage label |
| Dismiss forever on first visit | Persistent or session-scoped visibility |
| Different messages on web vs CLI | One canonical copy, medium-appropriate formatting |
| "Beta" in UI but "stable" in docs | Single stage vocabulary everywhere |
| Blocking modal that prevents all use | Visible banner; block only for irreversible harm if needed |
| Color-only red border | Text + icon/label + `role="status"` or stderr prefix |

## Cross-References

- Document stability in README and docs: [document-project](../document-project/SKILL.md)
- Verify web banners in the browser: [browser-test](../browser-test/SKILL.md)
- Capture banner screenshots for docs: [document-screenshots](../document-screenshots/SKILL.md)

## Additional Resources

- Surface-specific examples: [examples.md](examples.md)
- Pre-ship checklist: [checklist.md](checklist.md)
