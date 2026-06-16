# Security Audit Checklists

Reference for [SKILL.md](SKILL.md). Work through every applicable item — mark N/A only with evidence.

## Phase 1 — Secrets and Credentials

- [ ] Committed `.env`, `.pem`, `.key`, `credentials.json`, `id_rsa`, kubeconfig
- [ ] Hardcoded API keys, tokens, passwords, connection strings in source
- [ ] Secrets in test fixtures, examples, or docs that mirror production patterns
- [ ] Secrets in Dockerfiles, compose files, Helm values, Terraform `*.tfvars`
- [ ] Secrets in CI workflow files or GitHub Actions env blocks
- [ ] Secrets in git history (even if removed from HEAD)
- [ ] Logs, error messages, or debug endpoints printing secrets
- [ ] Client-side exposure: secrets in frontend bundles, mobile apps, or public repos
- [ ] Weak or default credentials in config templates
- [ ] `.gitignore` gaps allowing secret files to be tracked

**Patterns to grep**: `password`, `secret`, `api[_-]?key`, `token`, `BEGIN (RSA |OPENSSH )?PRIVATE KEY`, `AKIA`, `ghp_`, `sk-`, `xoxb-`, connection strings with embedded passwords

## Phase 2 — Dependencies and Supply Chain

- [ ] Known CVEs in direct dependencies (run package-manager audit tools)
- [ ] Known CVEs in transitive dependencies
- [ ] Unpinned or floating versions in production (`*`, `latest`, `^` without lockfile discipline)
- [ ] Lockfile integrity — committed and current
- [ ] Typosquatting / suspicious package names
- [ ] Install scripts (`postinstall`, `preinstall`) with network or shell execution
- [ ] Git dependencies or tarball URLs without integrity hashes
- [ ] Outdated base images in Dockerfiles
- [ ] Unpinned GitHub Actions (`@main`, `@master`, mutable tags)
- [ ] Third-party scripts loaded without SRI (CDN JS)

## Phase 3 — Application Code

### Injection

- [ ] SQL injection — string concatenation in queries; missing parameterization
- [ ] Command injection — `exec`, `system`, `subprocess`, `child_process` with user input
- [ ] LDAP / XPath / NoSQL injection
- [ ] Template injection (SSTI) in Jinja, ERB, etc.
- [ ] Header injection / response splitting
- [ ] Log injection / CRLF in logs

### Authentication and Sessions

- [ ] Missing authentication on sensitive routes
- [ ] Weak password policy or no rate limiting on login
- [ ] Session fixation, predictable session IDs
- [ ] Missing `HttpOnly`, `Secure`, `SameSite` on session cookies
- [ ] JWT: `none` algorithm, weak secret, missing expiry, sensitive data in payload
- [ ] Password storage: plaintext, MD5, SHA1 without salt; missing bcrypt/argon2/scrypt
- [ ] MFA bypass paths
- [ ] OAuth misconfiguration: open redirects, state parameter missing, scope escalation

### Authorization

- [ ] IDOR — object access without ownership check
- [ ] Missing role checks on admin endpoints
- [ ] Horizontal privilege escalation between tenants/users
- [ ] Vertical privilege escalation (user → admin)
- [ ] Mass assignment — accepting unexpected fields on update/create
- [ ] Function-level access control gaps in GraphQL resolvers, RPC handlers

### Cryptography

- [ ] Hardcoded encryption keys or IVs
- [ ] ECB mode, deprecated algorithms (DES, RC4)
- [ ] `Math.random()` for security-sensitive values
- [ ] TLS verification disabled (`rejectUnauthorized: false`, `verify=False`)
- [ ] Insufficient key length

### Deserialization and Parsing

- [ ] Unsafe `pickle`, `yaml.load` (without Loader), `unserialize`, `ObjectInputStream`
- [ ] XML external entity (XXE) in XML parsers
- [ ] Prototype pollution in JavaScript object merges

### File and Path

- [ ] Path traversal (`../`) in file read/write/delete
- [ ] Unrestricted file upload — type, size, content not validated
- [ ] Symlink following in archive extraction (zip slip)
- [ ] Serving user-uploaded files with executable MIME types

### Business Logic

- [ ] Race conditions on balance, inventory, or quota operations
- [ ] Replay of state-changing requests without idempotency
- [ ] Price/quantity manipulation via client-controlled fields

## Phase 4 — API, Web, and Client

- [ ] Missing or overly permissive CORS (`Access-Control-Allow-Origin: *` with credentials)
- [ ] CSRF on cookie-authenticated state-changing endpoints
- [ ] Reflected/stored/DOM-based XSS
- [ ] Open redirects in login/logout/OAuth flows
- [ ] SSRF in URL fetchers, webhooks, image proxies, PDF generators
- [ ] GraphQL: introspection in production, depth/complexity bombs, batching abuse
- [ ] REST: verbose error bodies, missing pagination limits, enumeration via sequential IDs
- [ ] WebSocket auth missing or message-level authz gaps
- [ ] Missing security headers: CSP, HSTS, X-Content-Type-Options, X-Frame-Options
- [ ] Clickjacking on sensitive actions
- [ ] Sensitive data in URL query strings (tokens, PII)

## Phase 5 — Infrastructure, Containers, IaC, CI/CD

### Docker / Containers

- [ ] Running as root in container
- [ ] Secrets baked into image layers
- [ ] `--privileged`, excessive capabilities, host namespace sharing
- [ ] Published ports exposing internal services unnecessarily
- [ ] Missing resource limits (DoS via memory/CPU exhaustion)

### Kubernetes / Orchestration

- [ ] Overly broad RBAC (`cluster-admin` for apps)
- [ ] Secrets in plain ConfigMaps
- [ ] `hostPath` mounts, `hostNetwork: true` without justification
- [ ] Missing network policies

### Terraform / Cloud IaC

- [ ] Public S3 buckets / storage accounts
- [ ] Security groups open to `0.0.0.0/0` on admin ports
- [ ] IAM policies with `*` actions or resources
- [ ] Encryption at rest disabled
- [ ] State files containing secrets unencrypted

### CI/CD

- [ ] `pull_request_target` with untrusted code checkout
- [ ] Secrets available to fork PRs
- [ ] Overly broad `permissions:` in workflows
- [ ] Unpinned third-party actions
- [ ] Deploy keys or cloud credentials in workflow env without OIDC
- [ ] Artifact or cache poisoning vectors

## Phase 6 — Data Protection, Logging, Privacy

- [ ] PII in logs, metrics, or error trackers
- [ ] Missing encryption at rest for sensitive DB columns
- [ ] Missing encryption in transit between internal services
- [ ] Over-retention of personal data
- [ ] Debug endpoints enabled in production
- [ ] Backup files exposed (`.sql`, `.bak`, `.dump`)
- [ ] Verbose stack traces returned to clients

## Phase 7 — MCP and Agentic Surfaces

Apply [mcp-security](../mcp-security/SKILL.md) in full. Minimum checks:

- [ ] Tool handlers validate inputs with strict schema; reject unknown fields
- [ ] Per-call authorization — no ambient admin token
- [ ] Tool output sanitized — no secrets, no injection pivots
- [ ] Structured audit logging on allow, deny, and error paths
- [ ] Server sandboxed (container, non-root, network egress restricted)
- [ ] Tool definitions versioned/pinned
- [ ] Indirect prompt injection surfaces in tool descriptions and return values
- [ ] Blast radius documented per tool

## Phase 8 — Configuration and Deployment

- [ ] Default admin accounts or passwords in deployment docs
- [ ] Debug/development mode flags in production config
- [ ] Directory listing enabled on web server
- [ ] Missing rate limiting on auth and expensive endpoints
- [ ] Overly permissive file permissions on config or key files
- [ ] `robots.txt` or public repos revealing internal paths (informational)
- [ ] Missing WAF or reverse-proxy security controls where expected
- [ ] Timezone/locale leaks revealing infrastructure (informational)
