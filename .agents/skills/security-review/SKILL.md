---
name: security-review
description: This skill should be used when the user asks to "review security", "check for vulnerabilities", "add authentication", "handle user input", "work with secrets or API keys", "create an API endpoint", or "implement payment/sensitive features". Provides a security review checklist and defensive coding patterns.
---

# Security Review

Review code for security vulnerabilities and apply defensive coding patterns before shipping. Treat security as non-optional: rely on language- and framework-appropriate protections (parameterized queries, ORM validation, framework auth) rather than hand-rolled measures.

## When to Use

- Implementing authentication or authorization
- Handling user input, file uploads, or untrusted data
- Creating or modifying API endpoints
- Working with secrets, tokens, or credentials
- Implementing payment or other sensitive features
- Storing or transmitting sensitive data
- Integrating third-party APIs

## Review checklist

Walk the code against each area; fix confirmed issues as you go.

1. **Secrets management**
   - No hardcoded keys, tokens, or passwords in source.
   - Secrets come from environment variables / secret manager and are verified present at startup.
   - `.env`, `.env.*`, `*.pem`, `*.key` are git-ignored.
   - No secrets committed in git history.
   - Production secrets live in the hosting platform's secret store, not in the repo.

2. **Input validation**
   - Validate all untrusted input against a schema (whitelist, not blacklist).
   - Restrict file uploads by size, MIME type, and extension.
   - Never splice user input into queries, shells, or paths.
   - Keep error messages generic so they do not leak internals.

3. **SQL / injection prevention**
   - Use parameterized queries or an ORM/query builder everywhere.
   - Never concatenate user input into SQL, commands, or eval calls.

4. **Authentication & authorization**
   - Verify authorization (role/permission) before every sensitive operation, server-side.
   - Store tokens in `httpOnly`+`Secure`+`SameSite` cookies, not `localStorage`.
   - Enforce row-level / object-level visibility so users only read and write their own data.
   - Manage sessions securely and expire idle sessions.

5. **XSS & client-side**
   - Sanitize any user-provided HTML before rendering.
   - Set a Content-Security-Policy; avoid XSS-prone sinks (`dangerouslySetInnerHTML`-style patterns) where framework alternatives exist.

6. **CSRF & cross-site protection**
   - Put CSRF tokens on state-changing operations and set `SameSite=Strict` cookies.

7. **Rate limiting**
   - Apply rate limiting to all API endpoints; use stricter limits on expensive operations; consider per-user as well as per-IP limits.

8. **Sensitive data exposure**
   - Redact secrets, tokens, card data, and PII in logs.
   - Return generic errors to users; keep detailed errors and stack traces server-side only.
   - Avoid logging request bodies/headers that carry credentials.

9. **Dependency security**
   - Run the ecosystem's audit tool (`npm audit`, `pip-audit`, `cargo audit`, etc.) and fix findings.
   - Commit lock files and install reproducibly in CI.
   - Keep dependencies updated and enable automated security updates.

10. **Transport & headers**
    - Enforce HTTPS in production.
    - Set security headers: CSP, `X-Frame-Options`/`frame-ancestors`, `X-Content-Type-Options`, and appropriately restrictive CORS.

## Security testing

Add automated tests that exercise the security posture, not just the happy path:
- Unauthenticated access to a protected resource returns 401.
- Missing role returns 403.
- Invalid input returns 400.
- Excessive requests hit rate limits (429).

## Pre-deployment checklist

Before promoting anything to production, confirm:
secrets externalized; inputs validated; queries parameterized; XSS hardened; CSRF protected; auth and role checks present; rate limiting on; HTTPS enforced; security headers set; no sensitive data in errors or logs; dependencies clean; file uploads validated; CORS restrictive; object-level access control enabled.

## External references

Consult authoritative sources rather than memorizing platform quirks:
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheets (e.g. Input Validation, Auth Cheat Sheet, XSS)
- PortSwigger Web Security Academy: https://portswigger.net/web-security

### Reference Files
- **`references/web-security.md`** — concrete defensive patterns and anti-patterns for common stacks.

> Adapted from the `security-review` skill in `affaan-m/ECC` (MIT); generalized and reformatted for this workspace.