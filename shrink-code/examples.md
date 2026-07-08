# Shrink Code — Examples

## Example 1: Duplicate validation merged

**Before (28 LOC):**

```typescript
function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validateUserEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function createUser(email: string) {
  if (!validateUserEmail(email)) throw new Error("invalid email");
  // ...
}

function updateUser(email: string) {
  if (!isValidEmail(email)) throw new Error("invalid email");
  // ...
}
```

**After (18 LOC):**

```typescript
function validEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function createUser(email: string) {
  if (!validEmail(email)) throw new Error("invalid email");
  // ...
}

function updateUser(email: string) {
  if (!validEmail(email)) throw new Error("invalid email");
  // ...
}
```

**Critical parity:** Same rejection for invalid emails ✓

## Example 2: Pass-through wrapper removed

**Before:**

```python
class UserRepository:
    def __init__(self, db):
        self._db = db

    def get_user(self, user_id):
        return self._get_user_from_db(user_id)

    def _get_user_from_db(self, user_id):
        return self._db.query(User).filter_by(id=user_id).one_or_none()
```

**After:**

```python
class UserRepository:
    def __init__(self, db):
        self._db = db

    def get_user(self, user_id):
        return self._db.query(User).filter_by(id=user_id).one_or_none()
```

**Critical parity:** Same query, same return value ✓

## Example 3: Nested conditionals → guard clauses

**Before (14 LOC):**

```go
func process(req Request) error {
    if req.Valid {
        if req.User != nil {
            if req.User.Active {
                return doWork(req)
            } else {
                return ErrInactive
            }
        } else {
            return ErrNoUser
        }
    }
    return ErrInvalid
}
```

**After (10 LOC):**

```go
func process(req Request) error {
    if !req.Valid {
        return ErrInvalid
    }
    if req.User == nil {
        return ErrNoUser
    }
    if !req.User.Active {
        return ErrInactive
    }
    return doWork(req)
}
```

**Critical parity:** Same errors, same success path ✓

## Example 4: Switch → lookup table

**Before:**

```rust
fn status_label(code: u16) -> &'static str {
    if code == 200 { "ok" }
    else if code == 404 { "not found" }
    else if code == 500 { "error" }
    else { "unknown" }
}
```

**After:**

```rust
fn status_label(code: u16) -> &'static str {
    match code {
        200 => "ok",
        404 => "not found",
        500 => "error",
        _ => "unknown",
    }
}
```

Or for many variants, a `static` map when match arms grow.

**Critical parity:** Same labels per code ✓

## Example 5: Dead code removed

**Before:** `legacy_export_csv()` — 87 LOC, zero references in repo and no dynamic import.

**Action:** Confirm with ripgrep and test suite; delete file and unused imports.

**Critical parity:** All tests pass; no runtime callers ✓

## Example 6: What not to do

**Bad — golf hurts readability:**

```javascript
const f=(a,b,c)=>a?b(c):c;
```

**Bad — removed validation:**

```python
# Removed: if not user.is_admin: raise Forbidden
def delete_all_users():
    db.users.delete()
```

**Bad — merged unlike semantics:**

```typescript
// Combined parseDate and formatDate into one function with a flag — callers now ambiguous
function dateOp(s: string, format?: boolean) { ... }
```

## Savings report template

```markdown
## Shrink summary
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| LOC (`src/`) | 2,340 | 2,011 | -14% |
| Files | 48 | 45 | -3 |

## Preserved (critical)
- 142 unit tests pass
- REST API contracts unchanged
- Error codes and messages unchanged

## Removed or simplified
- `legacy_export_csv.py` deleted (unused)
- Merged 4 duplicate JSON serializers into `serialize_json`
- Collapsed nested auth checks in `middleware.py`
```
