# Document Screenshots — Examples

Adapt URLs and commands to the project. Prefer Makefile/CI scripts when present.

## Dev server URLs

| Stack | Start | Default URL |
|-------|-------|-------------|
| Vite (React, Vue, Svelte) | `npm run dev` | `http://localhost:5173` |
| Next.js | `npm run dev` | `http://localhost:3000` |
| Create React App | `npm start` | `http://localhost:3000` |
| Nuxt | `npm run dev` | `http://localhost:3000` |
| Angular | `ng serve` | `http://localhost:4200` |
| Rails | `bin/rails server` | `http://localhost:3000` |
| Django | `python manage.py runserver` | `http://localhost:8000` |
| Flask | `flask run` | `http://localhost:5000` |
| Docker Compose | `docker compose up web` | check `ports:` in compose file |

## Shot list example

Documenting a task manager app:

| Filename | URL / state | Doc file |
|----------|-------------|----------|
| `docs/images/home-task-list.png` | `/` logged in, sample tasks | `docs/features/tasks.md` |
| `docs/images/task-create-modal.png` | Click "New task", modal open | `docs/features/tasks.md` |
| `docs/images/task-empty-state.png` | `/` with zero tasks | `docs/getting-started.md` |

## MCP capture sequence

1. `browser_navigate` → `http://localhost:5173`
2. `browser_lock` → `action: "lock"`
3. `browser_snapshot` → confirm app shell loaded
4. `browser_take_screenshot` → `filename: "docs/images/home-task-list.png"`
5. `browser_click` → "New task" button ref from snapshot
6. `browser_snapshot` → confirm modal visible
7. `browser_take_screenshot` → `filename: "docs/images/task-create-modal.png"`
8. `browser_lock` → `action: "unlock"`

## Element vs full-page

```text
# Component only (settings panel)
browser_take_screenshot:
  filename: docs/images/settings-panel.png
  ref: <ref from snapshot>

# Entire scrollable page (long docs site)
browser_take_screenshot:
  filename: docs/images/docs-home-full.png
  fullPage: true
```

## Markdown embed patterns

From `docs/features/tasks.md`:

```markdown
## Task list

The home view shows open tasks grouped by project.

![Task list with three sample items and the new-task button in the header](../images/home-task-list.png)
```

From `README.md` (link into docs instead of duplicating images):

```markdown
See [Tasks](docs/features/tasks.md) for screenshots of the task list and create flow.
```

## Docker (with docker skill)

```bash
docker compose up -d web
# Map e.g. 3000:3000 — capture http://localhost:3000
```

## Replacing stale screenshots

1. Grep for the old filename: `rg 'old-dashboard.png' docs/`
2. Capture the new image to the same path (or a new name and update all references)
3. `git add docs/images/` and the updated markdown in one commit
