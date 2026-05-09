---
name: tdd-workflow
description: "Test-Driven Development workflow: RED-GREEN-REFACTOR with git checkpoints. Use when: implementing a new feature, fixing a bug, or adding tests to existing code. Enforces write-tests-first discipline with 80%+ coverage gate. Derived from Everything Claude Code (https://github.com/affaan-m/everything-claude-code)."
user-invocable: false
---

# Test-Driven Development Workflow

This skill ensures all code development follows TDD principles with comprehensive
test coverage. Tests are not optional -- they are the safety net that enables
confident refactoring, rapid development, and production reliability.

## When to Activate

- Writing new features or functionality
- Fixing bugs or issues (write a reproducer test first)
- Refactoring existing code
- Adding API endpoints
- Any task where an acceptance criterion can be expressed as a test

## Core Principles

### 1. Tests BEFORE Code

ALWAYS write tests first, then implement code to make tests pass.

### 2. Coverage Requirements

- Minimum 80% coverage (unit + integration + E2E)
- All edge cases covered
- Error scenarios tested
- Boundary conditions verified

### 3. Test Types

**Unit Tests**: Individual functions and utilities, component logic, pure functions,
helpers and utilities.

**Integration Tests**: API endpoints, database operations, service interactions,
external API calls.

**E2E Tests**: Critical user flows, complete workflows, UI interactions.

### 4. Git Checkpoints

If the repository is under Git, create a checkpoint commit after each TDD stage.
Do not squash or rewrite these checkpoint commits until the workflow is complete.
Each checkpoint commit message must describe the stage and exact evidence captured.
Count only commits created on the current active branch for the current task.

Preferred compact workflow:
- One commit for failing test added and RED validated
- One commit for minimal fix applied and GREEN validated
- One optional commit for refactor complete

## TDD Workflow Steps

### Step 1 -- Write User Journeys

Before any code or test, write user journeys:

```
As a [role], I want to [action], so that [benefit]

Example:
As a user, I want to search for products semantically,
so that I can find relevant items even without exact keywords.
```

### Step 2 -- Generate Test Cases

For each user journey, create comprehensive test cases:

```
describe('Semantic Search', () => {
  it('returns relevant results for query')
  it('handles empty query gracefully')
  it('falls back to substring search when service unavailable')
  it('sorts results by similarity score')
})
```

Write the full test stubs (describe/it structure) with assertions. Do NOT write
production code yet.

### Step 3 -- RED: Run Tests (They Must Fail)

Run the test suite. This step is MANDATORY and is the RED gate for all production
changes.

Before modifying business logic or other production code, you must verify a valid
RED state via one of these paths:

**Runtime RED:**
- The relevant test target compiles successfully
- The new or changed test is actually executed
- The result is RED (test fails)

**Compile-time RED:**
- The new test newly instantiates, references, or exercises the buggy code path
- The compile failure is itself the intended RED signal

In either case, the failure must be caused by the intended business-logic bug,
undefined behavior, or missing implementation. A test that was only written but
not compiled and executed does NOT count as RED.

Do not edit production code until this RED state is confirmed.

If the repository is under Git, create a checkpoint commit after RED is validated:
- Commit message format: `test: add reproducer for <feature or bug>`

### Step 4 -- Implement Minimal Code

Write the minimum code necessary to make tests pass:

- Do not add features beyond what the tests require
- Do not refactor at this stage
- Stage the minimal fix but defer the checkpoint commit until GREEN is validated

### Step 5 -- GREEN: Run Tests Again

Rerun the same relevant test target after the fix and confirm the previously
failing test is now GREEN.

Only after a valid GREEN result may you proceed to refactor.

If the repository is under Git, create a checkpoint commit immediately after GREEN:
- Commit message format: `fix: <feature or bug>`

### Step 6 -- Refactor

Improve code quality while keeping tests green:
- Remove duplication
- Improve naming
- Optimize performance
- Enhance readability

If the repository is under Git, create a checkpoint commit after refactoring:
- Commit message format: `refactor: clean up after <feature or bug> implementation`

### Step 7 -- Verify Coverage

Run the coverage report and verify 80%+ achieved across:
- Branches
- Functions
- Lines
- Statements

Coverage config (Jest example):
```json
{
  "coverageThresholds": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    }
  }
}
```

## Test File Organization

```
src/
+-- components/
|   +-- Button/
|       +-- Button.tsx
|       +-- Button.test.ts        (unit tests alongside source)
+-- app/
|   +-- api/
|       +-- users/
|           +-- route.ts
|           +-- route.test.ts     (integration tests)
+-- e2e/
    +-- users.spec.ts             (E2E tests, critical user flows)
    +-- auth.spec.ts
```

## Testing Patterns by Framework

### Python (pytest)
```python
def test_returns_results_for_valid_query():
    result = search("login")
    assert len(result) > 0
    assert result[0]["score"] > 0.7

def test_raises_on_empty_query():
    with pytest.raises(ValueError, match="query cannot be empty"):
        search("")
```

### TypeScript (Jest/Vitest)
```typescript
describe('search', () => {
  it('returns results for valid query', async () => {
    const results = await search('login')
    expect(results.length).toBeGreaterThan(0)
    expect(results[0].score).toBeGreaterThan(0.7)
  })

  it('raises on empty query', async () => {
    await expect(search('')).rejects.toThrow('query cannot be empty')
  })
})
```

### Go (testing)
```go
func TestSearch_ReturnsResultsForValidQuery(t *testing.T) {
    results, err := Search("login")
    if err != nil { t.Fatal(err) }
    if len(results) == 0 { t.Error("expected results") }
}
```

## Mocking External Dependencies

Isolate unit tests from I/O:
- Database: use an in-memory DB or mock the repository layer
- HTTP services: use a test server or mock the HTTP client
- Time/clocks: inject a fake clock
- File system: use temp directories or mock the FS interface

Example (Python):
```python
@pytest.fixture
def mock_db(monkeypatch):
    db = FakeDatabase()
    monkeypatch.setattr("myapp.db.connection", db)
    return db
```

## Common Mistakes to Avoid

**WRONG -- Testing implementation details:**
```python
# Don't assert internal state
assert service._cache["key"] == expected
```
**CORRECT -- Test user-visible behavior:**
```python
# Assert what the caller observes
assert service.get("key") == expected
```

**WRONG -- Brittle selectors (UI tests):**
```
click(".css-xyz-generated-class")
```
**CORRECT -- Semantic selectors:**
```
click("button[aria-label='Submit']")
click("[data-testid='submit-button']")
```

**WRONG -- Tests that depend on each other:**
```python
def test_create(): user = create_user("alice")
def test_update(): update_user("alice", ...)  # depends on test_create state
```
**CORRECT -- Independent tests (each test sets up its own data):**
```python
def test_create(): user = create_user("alice"); assert ...
def test_update(): user = create_user("alice"); update_user(user.id, ...); assert ...
```

## Continuous Testing

Run tests in watch mode during development:
```
npm test -- --watch       # Jest
pytest-watch              # Python
go test ./... -watch      # Go (with gotestsum)
```

Pre-commit gate (run before every commit):
```
npm test && npm run lint
pytest && ruff check .
```

## Best Practices

1. Write tests first -- always TDD
2. One assertion per test -- focus on single behavior
3. Descriptive test names -- explain what is tested and expected outcome
4. Arrange-Act-Assert -- clear test structure
5. Mock external dependencies -- isolate unit tests from I/O
6. Test edge cases -- null, empty, boundary values
7. Test error paths -- not just happy paths
8. Keep unit tests fast -- each unit test under 50ms
9. Clean up after tests -- no side effects between tests
10. Review coverage reports -- identify untested branches

## Success Metrics

- 80%+ code coverage achieved
- All tests passing (green)
- No skipped or disabled tests
- Fast test execution (under 30s for unit tests)
- E2E tests cover critical user flows
- Tests catch bugs before production

**STOP here if RED is not confirmed. Never write production code before seeing RED.**

### Step 3a -- Git checkpoint: RED confirmed

```
git add <test files>
git commit -m "test: add reproducer for <feature>"
```

## Step 4 -- Implement minimal production code

Write the minimum code to make the failing tests pass.
- No over-engineering.
- No features not required by the current tests.
- If you find yourself adding untested code: stop, write the test first.

## Step 5 -- GREEN: Confirm all tests pass

Run the exact same test target from Step 3. All tests must pass.
- If any test still fails: fix the production code, not the test.
- If you changed a test to make it pass: that is a RED flag. Stop and reassess.

### Step 5a -- Git checkpoint: GREEN confirmed

```
git add <production code files>
git commit -m "feat: implement <feature>"
```

## Step 6 -- Refactor

Improve code quality without changing behavior:
- Remove duplication
- Improve naming (functions, variables, modules)
- Extract helper functions if complexity warrants
- Apply language idioms

Re-run tests after every refactor step. Tests must stay green throughout.

### Step 6a -- Git checkpoint: refactor complete

```
git add <modified files>
git commit -m "refactor: clean up <feature>"
```

## Step 7 -- Verify coverage gate

Run coverage analysis:
```
# Python:
python -m pytest --cov=<module> --cov-report=term-missing

# JavaScript/TypeScript:
npx jest --coverage
```

**Coverage threshold: 80% minimum on branches, functions, lines, and statements.**

If below 80%: identify uncovered paths, write tests for them, repeat from Step 3.

# Test Organization

```
tests/
  unit/          # Pure functions, no I/O
  integration/   # DB, network, external services (use fixtures/mocks)
  e2e/           # Full user journey (Playwright, Cypress, httpx)
```

Name test files: `test_<module>.py` / `<module>.test.ts`
Name test functions: `test_<action>_<scenario>` (e.g. `test_login_invalid_password`)

<gates>

# Rules

- RED gate is mandatory. No exceptions.
- Never modify a test to make it pass -- fix the production code.
- Git checkpoint after each phase (RED, GREEN, REFACTOR).
- 80% coverage is a gate, not a suggestion.
- Tests must be runnable locally: no cloud-only test infrastructure.
- Run tests in the target project's intended execution environment. Use Docker only when the target repo is already containerized; do not require it for this workflow repo.

</gates>

# Delegation

Invoke the `quality` agent after Step 7 for final verification:
- Static analysis (ruff/pylint/eslint)
- Type checking (mypy/tsc)
- Security scan

# References

- [Test templates by language](./assets/test-templates.md)
- [Coverage configuration examples](./assets/coverage-config.md)
