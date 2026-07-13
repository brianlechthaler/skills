# Experimental Warning — Checklist

Use before merge or release when software is pre-release.

## Message and policy

- [ ] Single release stage chosen (experimental / alpha / beta / preview)
- [ ] Canonical warning copy written and approved
- [ ] Consequences stated (breaking changes, data loss, no production guarantee)
- [ ] Feedback or docs URL included when available
- [ ] README and docs use the same stage name and severity as runtime UI

## Web UI

- [ ] Banner in root layout, visible on all routes
- [ ] Appears above nav and primary content
- [ ] `role="status"` or `role="alert"` and `aria-live` where appropriate
- [ ] Contrast meets WCAG AA
- [ ] Not color-only (text + visual indicator)
- [ ] Survives client-side navigation without disappearing

## CLI / TUI

- [ ] stderr warning on startup before interactive work
- [ ] Stage mentioned in `--help` and `--version` output
- [ ] TUI shows persistent header or panel on every screen
- [ ] `--quiet` behavior documented if warnings are suppressible

## Desktop / mobile

- [ ] Warning on first screen or persistent chrome
- [ ] About/settings screen repeats stage and limitations

## API / SDK

- [ ] OpenAPI or API reference description includes stability notice
- [ ] Generated SDK docs inherit the same wording
- [ ] Optional response header documented if used

## Verification

- [ ] Cold-start test on each surface
- [ ] Screen reader or accessibility spot-check (web)
- [ ] No surface contradicts another on stage or severity
- [ ] Screenshots updated in docs if UI changed ([document-screenshots](../document-screenshots/SKILL.md))
