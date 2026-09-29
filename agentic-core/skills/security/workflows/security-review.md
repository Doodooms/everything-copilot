---
id: security-review
description: 'Perform a static security review of authentication, authorization, input handling,
  API boundaries, secrets, data exposure, and security evidence.'
invoke_for:
- changes affecting authentication, authorization, input handling, API boundaries, secrets, or sensitive data
- static security evidence review before a release or deployment
avoid_for:
- dynamic security testing, production fixes, architecture ownership, or final non-security
  acceptance or merge decisions
references: []
---
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Scope the review

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read and #tool:search to identify the changed files, their security-relevant dependencies, and tests covering the changed behavior.
2. Record the review boundary, relevant data and authority flows, and any areas that cannot be inspected. Do not expand into production fixes, architecture ownership, or dynamic test campaigns.

## Step 2 - Apply the security checklist

1. When available, use #tool:mcp_semgrep_semgrep_scan on the changed source files first; treat its output as a source of findings, not as proof of safety or a replacement for manual review. Record unavailable or unsupported scans as unknown.
2. Use #tool:execute only for narrow security checks, then inspect each applicable category below. For every result, record direct evidence with the file path and line number.

  - **1. Secrets Management**

    - **FAIL: NEVER hardcode secrets**
      ```
      # BAD
      API_KEY = "sk-proj-xxxxx"
      DB_PASSWORD = "password123"
      ```

    - **PASS: ALWAYS use environment variables**
      ```
      # GOOD
      import os
      api_key = os.environ["OPENAI_API_KEY"]  # Python
      # const apiKey = process.env.OPENAI_API_KEY  // Node.js

      # Fail fast if missing
      if not api_key:
          raise RuntimeError("OPENAI_API_KEY not configured")
      ```

    - **Verification Steps**
      - [ ] No hardcoded API keys, tokens, or passwords
      - [ ] All secrets in environment variables
      - [ ] `.env` / `.env.local` in `.gitignore`
      - [ ] No secrets in git history
      - [ ] Production secrets in hosting platform vault (not in code)


  - **2. Input Validation**

    - **FAIL: Using raw user input without validation**
      ```
      # BAD -- trusting user input directly
      def create_user(email, age):
          db.execute(f"INSERT INTO users VALUES ('{email}', {age})")
      ```

    - **PASS: Validate all inputs with a schema**
      ```
      # GOOD -- validate first, use after
      from pydantic import BaseModel, EmailStr

      class CreateUserRequest(BaseModel):
          email: EmailStr
          name: str  # pydantic enforces str
          age: int

      def create_user(body: CreateUserRequest):
          db.create(email=body.email, name=body.name, age=body.age)
      ```

    - **File Upload Validation**
      ```python
      # GOOD -- check size, type, and extension
      MAX_SIZE = 5 * 1024 * 1024  # 5 MB
      ALLOWED_TYPES = {"image/jpeg", "image/png"}
      ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


      def validate_upload(file):
          if file.size > MAX_SIZE:
              raise ValueError("File too large (max 5MB)")
          if file.content_type not in ALLOWED_TYPES:
              raise ValueError("Invalid file type")
          ext = os.path.splitext(file.filename)[1].lower()
          if ext not in ALLOWED_EXTENSIONS:
              raise ValueError("Invalid file extension")
      ```

    - **Verification Steps**
      - [ ] All user inputs validated with schemas
      - [ ] File uploads restricted (size, type, extension)
      - [ ] No direct use of raw user input in queries
      - [ ] Whitelist validation (not blacklist)
      - [ ] Error messages do not leak sensitive info


  - **3. SQL Injection Prevention**

    - **FAIL: String concatenation in queries**
      ```python
      # BAD -- SQL injection vulnerability
      query = f"SELECT * FROM users WHERE email = '{user_email}'"
      db.execute(query)
      ```

    - **PASS: Always use parameterized queries**
      ```python
      # GOOD -- parameterized
      db.execute("SELECT * FROM users WHERE email = %s", (user_email,))

      # GOOD -- ORM (SQLAlchemy, Django ORM, Prisma, etc.)
      user = User.objects.filter(email=user_email).first()
      ```

    - **Verification Steps**
      - [ ] All database queries use parameterized queries or ORM
      - [ ] No string concatenation in SQL
      - [ ] No `eval()` or `exec()` on user-controlled strings
      - [ ] No `shell=True` with user-controlled input


  - **4. Authentication and Authorization**

    - **Token Storage**
      ```
      # BAD -- tokens in localStorage (vulnerable to XSS)
      localStorage.setItem("token", token)

      # GOOD -- httpOnly cookies (inaccessible to JavaScript)
      Set-Cookie: token=<value>; HttpOnly; Secure; SameSite=Strict; Max-Age=3600
      ```

    - **Authorization Checks**
      ```python
      # GOOD -- always verify authorization before sensitive operations
      def delete_resource(resource_id: str, requester_id: str):
          requester = db.users.get(requester_id)
          if requester.role != "admin":
              raise PermissionError("Unauthorized")
          db.resources.delete(resource_id)
      ```

    - **Database-Level Authorization**
      Enable row-level security at the database layer so application bugs cannot
      expose another user's data:
      ```sql
      -- PostgreSQL example (enable per table)
      ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
      CREATE POLICY "users_own_documents"
        ON documents FOR SELECT
        USING (owner_id = current_user_id());
      ```

    - **Verification Steps**
      - [ ] Tokens stored in httpOnly cookies (not localStorage)
      - [ ] Authorization checks before sensitive operations
      - [ ] Role-based access control implemented
      - [ ] Session invalidated on logout and password change
      - [ ] Rate limiting or lockout on login attempts


  - **5. XSS Prevention**

    - **FAIL: Rendering raw user content**
      ```
      # BAD -- renders any HTML the user provides
      <div dangerouslySetInnerHTML={{ __html: userComment }} />
      ```

    - **PASS: Sanitize or escape HTML**
      ```
      # GOOD -- sanitize (allow only safe tags/attrs)
      import bleach
      clean = bleach.clean(user_html, tags=["b","i","em","strong","p"], attributes={})
      ```

    - **Content Security Policy**
      Always set a restrictive CSP header in production:
      ```
      Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;
      ```

    - **Verification Steps**
      - [ ] User-provided HTML sanitized before rendering
      - [ ] CSP headers configured
      - [ ] No unvalidated dynamic content rendering


  - **6. CSRF Protection**

    - **PASS: CSRF tokens on state-changing operations**
      ```python
      # Django (built-in) -- {% csrf_token %} in forms, enforced by middleware
      # Flask -- flask-wtf CSRFProtect()
      # Express -- csurf middleware

      # Also: SameSite=Strict on all session cookies
      Set-Cookie: session=<value>; HttpOnly; Secure; SameSite=Strict
      ```

    - **Verification Steps**
      - [ ] CSRF tokens on all state-changing operations (POST, PUT, DELETE, PATCH)
      - [ ] SameSite=Strict on all cookies
      - [ ] State-changing endpoints reject GET requests


  - **7. Rate Limiting**

    - **PASS: Rate limit all API endpoints**
      ```python
      # Python (Flask-Limiter)
      from flask_limiter import Limiter
      limiter = Limiter(app, default_limits=["100 per 15 minutes"])

      @app.route("/api/search")
      @limiter.limit("10 per minute")   # stricter for expensive ops
      def search(): ...

      # Node.js (express-rate-limit)
      const limiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 100 })
      app.use("/api/", limiter)
      ```

    - **Verification Steps**
      - [ ] Rate limiting on all public API endpoints
      - [ ] Stricter limits on authentication and expensive operations
      - [ ] IP-based rate limiting
      - [ ] User-based rate limiting for authenticated routes


  - **8. Sensitive Data Exposure**

    - **FAIL: Logging sensitive data**
      ```python
      # BAD
      logging.info(f"User login: email={email}, password={password}")
      logging.info(f"Payment: card={card_number}, cvv={cvv}")
      ```

    - **PASS: Redact sensitive fields**
      ```python
      # GOOD
      logging.info(f"User login: email={email}, user_id={user_id}")
      logging.info(f"Payment processed: last4={card.last4}, user_id={user_id}")
      ```

    - **Error Message Leakage**
      ```python
      # BAD -- exposes internals
      except Exception as e:
          return {"error": str(e), "traceback": traceback.format_exc()}, 500

      # GOOD -- generic message for clients, full details in server logs
      except Exception as e:
          logging.error("Internal error", exc_info=True)
          return {"error": "An error occurred. Please try again."}, 500
      ```

    - **Verification Steps**
      - [ ] No passwords, tokens, or secrets in logs
      - [ ] Error messages are generic for users
      - [ ] Detailed errors only in server logs (not returned to clients)
      - [ ] No stack traces exposed to users


  - **9. Server-Side Request Forgery (SSRF)**

    - **PASS: Validate and allowlist user-supplied URLs**
      ```python
      # BAD -- fetches any URL the user provides
      resp = requests.get(user_supplied_url)

      # GOOD -- allowlist or validate URL
      from urllib.parse import urlparse

      ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}


      def safe_fetch(url: str) -> bytes:
          parsed = urlparse(url)
          if parsed.hostname not in ALLOWED_HOSTS:
              raise ValueError(f"Host not allowed: {parsed.hostname}")
          return requests.get(url, timeout=5).content
      ```

    - **Verification Steps**
      - [ ] User-supplied URLs validated against an allowlist before fetching
      - [ ] Internal network addresses blocked (169.254.x.x, 10.x.x.x, localhost)
      - [ ] HTTP redirect following limited or disabled for user-supplied URLs


  - **10. Dependency Security**

    - **Run dependency audit**
      ```bash
      pip audit           # Python
      npm audit           # Node.js
      cargo audit         # Rust
      bundle audit        # Ruby
      ```

    - **Lock file hygiene**
      ```bash
      # ALWAYS commit lock files
      git add requirements.lock package-lock.json Cargo.lock Gemfile.lock
      # Use locked installs in CI
      pip install --require-hashes -r requirements.lock
      npm ci   # instead of npm install
      ```

    - **Verification Steps**
      - [ ] Dependencies up to date
      - [ ] No known CVEs in direct dependencies (audit clean)
      - [ ] Lock files committed and used in CI
      - [ ] Dependabot or similar alerts enabled on GitHub

  - **11. Cross-Origin Resource Sharing (CORS)**

    - For authenticated or sensitive responses, allow only explicit trusted origins; never reflect an unvalidated `Origin` value.
    - Use `Access-Control-Allow-Origin: *` only when public, non-credentialed access is explicitly intended. A wildcard origin MUST NOT be combined with credentialed requests.
    - When returning an allowlisted origin dynamically, include `Vary: Origin` so caches distinguish responses by origin.
    - CORS is not authorization and MUST NOT replace server-side access checks or CSRF protection.

    - **Verification Steps**
      - [ ] Allowed origins match the intended public or authenticated resource contract
      - [ ] Credentialed responses use an explicit origin and explicit allowed headers/methods
      - [ ] Dynamic origin responses include `Vary: Origin`
      - [ ] Untrusted origins cannot read sensitive responses

## Step 3 - Assess evidence and classify results

1. Review existing tests and runtime evidence for each applicable control. Do not edit production code or create dynamic test campaigns here; route those tasks to the `security-testing` workflow through the parent `security` skill.
2. Mark a control `PASS` only when inspected evidence supports it, `FAIL` when evidence demonstrates a defect, `N/A` with a reason when it does not apply, and `UNKNOWN` when the available evidence cannot decide it.
3. For each finding, record severity, affected path and line, the trust boundary or abuse case, evidence, and a concrete remediation direction. Do not promote a scanner alert to a confirmed finding without checking the source context.

## Step 4 - Return the security review

1. Return a structured report with the reviewed scope, overall status (`pass`, `fail`, `partial`, or `unknown`), checks and evidence, findings with severity and locations, unverified controls, and residual risk.
2. Include deployment-specific controls only when deployment is in scope; mark unavailable evidence `UNKNOWN` instead of treating a checklist item as passed.
3. Send the findings to the parent Orchestrator or Reviewer for acceptance. Report severity and release impact, but do not make merge or deployment decisions from this workflow.
</workflow>
