# Static security review controls

Load this reference only while applying the `security-review` workflow. Scope each control to the changed trust boundary; a generic checklist does not make every control applicable or prove a system secure.

## Review the boundary and data flow

Identify who controls each input, what identity and authority reach the operation, what data is read or changed, and which process or service receives it. Trace the implementation through relevant callers and dependencies. Distinguish evidence in the inspected code from assumptions about deployment, runtime configuration, and provider controls.

## Identity and authorization

- Check authentication where the contract requires an identity; verify token/session validation and lifecycle only for the affected flow.
- Enforce authorization for the specific object and action on every sensitive read or mutation. Default deny when no rule grants access. Check ownership/tenant boundaries; a role check at the route alone may not establish access to the selected object.
- Where the database supports row-level authorization, assess it as defense-in-depth only when relevant. Verify the application identity is propagated correctly and which owner/admin/background roles can bypass policies; database policies do not replace application authorization.
- For browser sessions, inspect cookie flags and CSRF controls in the actual framework and threat model. Token-storage choices are not universal substitutes for checking the full browser security design.

**GOOD:** resolve the requested record, verify the caller may access that record, then return or mutate it.

**BAD:** confirm that a caller is signed in or has a broad role, then trust a caller-supplied record ID without checking its owner or tenant.

**GOOD:** combine per-object application checks with correctly scoped database row policies when the data model and role setup support them.

**BAD:** assume row policies protect privileged connections or background jobs without verifying their database roles and principal context.

## Input, injection, and uploads

- Validate type, shape, size, range, and domain constraints at the trust boundary. Validate authority separately; a valid schema is not authorization.
- Use parameterized database operations or a safe query builder. For process execution, pass structured arguments to a fixed executable and constrain allowed operations; avoid shell interpretation of untrusted strings.
- For uploads, enforce size limits, inspect content rather than trusting the filename or declared MIME type, constrain allowed formats, generate storage names, and store outside executable/public paths unless public serving is required.

```text
GOOD: bind a validated user value as a query parameter.
BAD: interpolate the value into SQL or a shell command.
```

## Secrets, data exposure, and errors

- Keep credentials out of source, fixtures, command-line arguments, tool results, and logs. Prefer the deployment's approved secret manager or credential injection with least privilege and rotation. Environment variables are a possible delivery mechanism only when the host's exposure model and controls make them appropriate; do not treat them as universally safe.
- Avoid logging passwords, access/refresh tokens, session identifiers, private keys, or sensitive payloads. Return a caller-safe error and keep needed diagnostic details in access-controlled logs.
- Check that failures do not disclose file paths, stack traces, internal hostnames, query contents, or authorization details across the boundary.

**GOOD:** inject a narrowly scoped credential through the approved runtime secret mechanism and redact it from diagnostics.

**BAD:** commit a key, pass it as a process argument, or assume a generic `.env`/environment variable is protected without checking the host.

## Browser-facing controls

- XSS: rely on context-appropriate framework escaping/encoding by default. Sanitize only when the product intentionally accepts HTML, using a maintained sanitizer and a narrow allowlist. Review dangerous DOM sinks and URL/script contexts. A Content Security Policy can add defense-in-depth; it does not replace safe output handling.
- CSRF: for cookie-authenticated state-changing requests, verify the framework's CSRF defense or an equivalent token/origin control. `SameSite` is defense-in-depth; do not assume it always replaces the application's CSRF contract.
- Session cookies: use `Secure` over HTTPS and `HttpOnly` when client-side script need not read the session value; choose `SameSite`, lifetime, and invalidation behavior for the actual cross-site and login/logout flow.
- Cross-Origin Resource Sharing (CORS): allow only the origins required by the API contract; do not reflect arbitrary origins. Use a wildcard origin only for explicitly intended public, non-credentialed access; a wildcard origin MUST NOT be combined with credentialed requests. CORS is not authentication or authorization. If a response varies by an allowlisted origin, include `Vary: Origin` so caches respect that variation.

```text
GOOD: preserve framework output escaping; sanitize only a deliberate rich-text field.
BAD: render attacker-controlled HTML directly or disable escaping to make a display bug disappear.
```

```text
GOOD: authorize the API request on the server and configure CORS for the intended browser origins.
BAD: rely on a CORS allowlist as the access-control check for a sensitive operation, or return `Access-Control-Allow-Origin: *` on a credentialed response.
```

## Outbound requests and SSRF

For a user-influenced URL, validate scheme and host against the operation's intended allowlist, resolve and reject loopback/link-local/private destinations as required by the boundary, and constrain redirects and DNS changes. Apply timeouts and response-size bounds. Re-check each redirect destination; hostname string checks alone do not prevent alternate IP notation, DNS rebinding, or redirect-to-internal-network cases.

**GOOD:** allow a small set of service destinations and validate the resolved address and every redirect before connecting.

**BAD:** call `GET` on any supplied URL after checking only that its text begins with `https://`.

## Abuse limits and dependency evidence

- Apply request, payload, concurrency, and time limits according to resource cost and abuse risk. Use identity/account limits for authenticated expensive actions and network limits where appropriate; do not require identical rate limits on every endpoint.
- Inspect dependency alerts or audit output when the changed surface depends on affected packages or when the review scope requests a dependency audit. Record the manifest/lockfiles and scanner coverage. A clean scan is evidence about that scan's scope and database, not proof that all dependencies are safe.
- Verify lockfile and update policy only when dependency changes or the release boundary makes them relevant.

## Evidence and disposition

| Status | Meaning |
| --- | --- |
| `PASS` | Inspected evidence supports the control for the reviewed boundary. |
| `FAIL` | Evidence demonstrates a defect or missing required control. |
| `N/A` | The control does not apply; record why. |
| `UNKNOWN` | Required source, configuration, runtime, or scan evidence is unavailable or inconclusive. |

Do not mark an unseen deployment control `PASS`. For each finding, capture severity, path and line, boundary/abuse case, direct evidence, and remediation direction. Report scan/tool limits separately. This is static security evidence for the parent reviewer; it is not a dynamic penetration test or the final release/merge decision.

## Primary references

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
