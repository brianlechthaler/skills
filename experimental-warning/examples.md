# Experimental Warning — Examples

## Example 1: Full-stack web app (React)

**Situation:** SPA marked beta; users hit the dashboard immediately after login.

**Root layout banner:**

```tsx
export function ExperimentalBanner() {
  return (
    <div role="status" aria-live="polite" className="experimental-banner">
      <strong>Beta.</strong> This app is pre-release. Features may change or break
      without notice. Not recommended for production use.{" "}
      <a href="https://github.com/org/app/issues">Report issues</a>
    </div>
  );
}
```

Mount `<ExperimentalBanner />` once in the app shell above `<nav>` and `<main>`. Verify it remains after client-side route changes.

## Example 2: Python CLI

**Situation:** `mytool` is experimental; users run subcommands from scripts and interactively.

```python
import os
import sys

STAGE = "experimental"
WARNING = (
    f"warning: mytool is {STAGE} — not recommended for production; "
    "behavior may change without notice.\n"
)

def emit_warning() -> None:
    if os.environ.get("MYTOOL_QUIET"):
        return
    print(WARNING, file=sys.stderr, end="")

def main() -> None:
    emit_warning()
    # ... parse args and run
```

Add to argparse epilog: `f"Status: {STAGE} (pre-release)"`.

## Example 3: Go CLI with Cobra

```go
const stageWarning = "warning: shipctl is alpha — not recommended for production; APIs may change.\n"

func init() {
    if os.Getenv("SHIPCTL_QUIET") == "" {
        fmt.Fprint(os.Stderr, stageWarning)
    }
}
```

Run before `cobra.Execute()` so every invocation sees the warning unless quiet.

## Example 4: TUI (terminal UI)

**Situation:** Bubble Tea or similar full-screen TUI.

Render a one-line header on every model view:

```
┌─ ALPHA ─ Pre-release software; data loss possible. Not for production. ─┐
│                                                                          │
│   [ main TUI content ]                                                   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

Do not show the warning only on a splash screen that users skip after the first run.

## Example 5: OpenAPI description

```yaml
openapi: 3.1.0
info:
  title: Widget API
  version: 0.4.0
  description: |
    **Experimental (v0.x).** This API is unstable. Endpoints, schemas, and
    authentication may change without a major version bump. Not recommended
    for production integrations.
```

Mirror the same text in the developer portal landing page.

## Example 6: Inconsistent copy — fix

| Surface | Before (bad) | After (good) |
|---------|----------------|--------------|
| Web | "Beta — things might change" | "Beta. Pre-release; not for production. May break without notice." |
| CLI | (no warning) | Same sentence as web, stderr prefix |
| README | "Mostly stable" | "Beta — same limitations as in-app banner" |

**Result:** Users never get a false sense of stability from docs or one surface alone.
