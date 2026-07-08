# Simple Code — Examples

## Example 1: Inline instead of a single-use helper

**Verbose (9 lines):**

```python
def get_active_users(users):
    result = []
    for u in users:
        if u.active:
            result.append(u)
    return result

def filter_users(users):
    return get_active_users(users)
```

**Simple (3 lines):**

```python
def filter_users(users):
    return [u for u in users if u.active]
```

## Example 2: Guard clauses over nesting

**Verbose (12 lines):**

```typescript
function charge(user: User, amount: number) {
  if (user) {
    if (user.active) {
      if (amount > 0) {
        return billing.charge(user.id, amount);
      }
    }
  }
  throw new Error("invalid");
}
```

**Simple (6 lines):**

```typescript
function charge(user: User, amount: number) {
  if (!user?.active || amount <= 0) throw new Error("invalid");
  return billing.charge(user.id, amount);
}
```

## Example 3: Map instead of repeated branches

**Verbose:**

```go
func roleLabel(r string) string {
    if r == "admin" { return "Administrator" }
    if r == "user" { return "User" }
    if r == "guest" { return "Guest" }
    return "Unknown"
}
```

**Simple:**

```go
var roleLabels = map[string]string{"admin": "Administrator", "user": "User", "guest": "Guest"}

func roleLabel(r string) string {
    if l, ok := roleLabels[r]; ok { return l }
    return "Unknown"
}
```

## Example 4: No speculative abstraction

**Verbose — factory for one call site:**

```rust
trait Formatter { fn format(&self, n: i32) -> String; }
struct DecimalFormatter;
impl Formatter for DecimalFormatter {
    fn format(&self, n: i32) -> String { n.to_string() }
}
fn display(n: i32) -> String { DecimalFormatter.format(n) }
```

**Simple:**

```rust
fn display(n: i32) -> String { n.to_string() }
```

## Example 5: What not to do

**Bad — golf:**

```javascript
const f=(a,b)=>a.reduce((x,y)=>x+y,b);
```

**Bad — removed validation:**

```python
def delete_user(user_id):
    db.delete(user_id)  # removed: auth check
```

**Bad — duplicate logic:**

```typescript
function saveA(d: Data) { if (!d.id) throw new Error("id"); return api.post("/a", d); }
function saveB(d: Data) { if (!d.id) throw new Error("id"); return api.post("/b", d); }
```

**Better — one path:**

```typescript
function save(path: string, d: Data) {
  if (!d.id) throw new Error("id");
  return api.post(path, d);
}
```
