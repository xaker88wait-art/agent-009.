# Web security patterns and anti-patterns

Concrete, stack-agnostic guidance referenced by the security-review skill. Examples use TypeScript/Next-style syntax; apply the same principles in the project's actual stack.

## Secrets

Anti-pattern — hardcoded secrets in source:

```js
const apiKey = "sk-proj-xxxxx"      // never
const dbPassword = "password123"    // never
```

Pattern — read from environment and fail fast if missing:

```js
const apiKey = process.env.API_KEY
const dbUrl = process.env.DATABASE_URL
if (!apiKey) throw new Error("API_KEY not configured")
```

## Input validation

Validate a whole object against a schema before processing (whitelist). Example with a schema validator:

```js
const schema = { email: "string.email", name: "string.min:1.max:100", age: "int.min:0.max:150" }
// parse/throw on invalid input; never pass raw body into queries
```

File uploads: reject by size first (e.g. >5 MB), then MIME type, then extension whitelist. Do not rely on the browser-supplied type alone; validate server-side.

## SQL injection

Anti-pattern — string concatenation:

```js
const q = `SELECT * FROM users WHERE email = '${email}'` // vulnerable
```

Pattern — parameterized queries:

```sql
SELECT * FROM users WHERE email = $1   -- bound: [email]
```

Use ORM query builders properly; never build dynamic query text from user input.

## Authentication & authorization

Token storage: prefer `httpOnly` + `Secure` + `SameSite=Strict` cookies over `localStorage` (which is readable by XSS).

Authorization: re-check role/permission server-side before each sensitive operation; never trust client-supplied claims:

```js
if (requester.role !== "admin") return response(403)
```

Row-level access (example SQL):

```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "users update own data" ON users FOR UPDATE USING (auth.uid() = id);
```

## XSS

Sanitize user-provided HTML with a curated allow-list of tags/attributes before rendering. Set a Content-Security-Policy. Prefer framework escaping over raw-HTML sinks.

## CSRF

Send a CSRF token with state-changing requests and verify it server-side. Set `SameSite=Strict` (or `Lax`) on cookies.

## Rate limiting

Apply a rate limiter to API routes; use a stricter window for expensive or sensitive operations (search, auth, payments):

```js
limiter({ windowMs: 60_000, max: 10 }) // e.g. search: 10 requests/minute
```

## Logging & errors

Anti-pattern:

```js
console.log("login:", { email, password })     // never log secrets
return response(500, { error: err.message, stack: err.stack })  // leaks internals
```

Pattern:

```js
// redact: log userId and last4, not the raw card/credentials
return response(500, { error: "An error occurred." })
// detailed error only in server logs
```

## Dependency & tooling

- Run the ecosystem audit tool (`npm audit` / `pip-audit` / `cargo audit`).
- Commit lock files (`package-lock.json`, `poetry.lock`, `Cargo.lock`) and install reproducibly in CI.
- Enable automated dependency-update PRs (Dependabot) and a fixed, reviewed schedule for upgrades.

## Applies everywhere

Use these principles together with the platform's official security documentation (framework auth docs, RLS/Supabase docs, Next/Svelte/Vue security pages) rather than guessing at defaults.