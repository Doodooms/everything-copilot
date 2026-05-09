---
name: coding-standards
description: "Baseline cross-project coding conventions for naming, readability, immutability, and code-quality review. Use when: reviewing code quality, starting new modules, onboarding to conventions, or enforcing naming/structure consistency. Derived from Everything Claude Code (https://github.com/affaan-m/everything-claude-code)."
---

# Coding Standards & Best Practices

Baseline coding conventions applicable across projects.

<scope>
Use this skill for:
- Descriptive naming enforcement
- Immutability defaults
- Readability, KISS, DRY, and YAGNI enforcement
- Error-handling expectations and code-smell review

Do NOT use this skill as the primary source for:
- React composition, hooks, or rendering patterns -- use `frontend-patterns`
- Backend architecture, API design, or database layering -- use `backend-patterns` or `api-design`
- Domain-specific framework guidance when a narrower skill already exists
</scope>

## When to Activate

- Starting a new project or module
- Reviewing code for quality and maintainability
- Refactoring existing code to follow conventions
- Enforcing naming, formatting, or structural consistency
- Onboarding new contributors to coding conventions

## Code Quality Principles

### 1. Readability First
- Code is read more than written
- Clear variable and function names
- Self-documenting code preferred over comments
- Consistent formatting

### 2. KISS (Keep It Simple)
- Simplest solution that works
- Avoid over-engineering
- No premature optimization
- Easy to understand > clever code

### 3. DRY (Don't Repeat Yourself)
- Extract common logic into functions
- Create reusable components
- Share utilities across modules
- Avoid copy-paste programming

### 4. YAGNI (You Aren't Gonna Need It)
- Don't build features before they're needed
- Avoid speculative generality
- Add complexity only when required
- Start simple, refactor when needed

## TypeScript/JavaScript Standards

### Variable Naming

```typescript
// GOOD: Descriptive names
const userSearchQuery = 'active'
const isAuthenticated = true
const totalRevenue = 1000

// BAD: Unclear names
const q = 'active'
const flag = true
const x = 1000
```

### Function Naming

```typescript
// GOOD: Verb-noun pattern
async function fetchUserData(userId: string) { }
function calculateSimilarity(a: number[], b: number[]) { }
function isValidEmail(email: string): boolean { }

// BAD: Unclear or noun-only
async function user(id: string) { }
function similarity(a, b) { }
function email(e) { }
```

### Immutability Pattern (CRITICAL)

```typescript
// ALWAYS use spread operator
const updatedUser = { ...user, name: 'New Name' }
const updatedArray = [...items, newItem]

// NEVER mutate directly
user.name = 'New Name'  // BAD
items.push(newItem)     // BAD
```

### Error Handling

```typescript
// GOOD: Comprehensive error handling
async function fetchData(url: string) {
  try {
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    return await response.json()
  } catch (error) {
    console.error('Fetch failed:', error)
    throw new Error('Failed to fetch data')
  }
}

// BAD: No error handling
async function fetchData(url) {
  const response = await fetch(url)
  return response.json()
}
```

### Async/Await Best Practices

```typescript
// GOOD: Parallel execution when possible
const [users, orders, stats] = await Promise.all([
  fetchUsers(),
  fetchOrders(),
  fetchStats()
])

// BAD: Sequential when unnecessary
const users = await fetchUsers()
const orders = await fetchOrders()
const stats = await fetchStats()
```

### Type Safety

```typescript
// GOOD: Proper types
interface User {
  id: string
  name: string
  role: 'admin' | 'user' | 'guest'
  createdAt: Date
}

function getUser(id: string): Promise<User> { }

// BAD: Using 'any'
function getUser(id: any): Promise<any> { }
```

## File Organization

### Project Structure

```
src/
├── app/              # Entry points / pages / routes
├── components/       # Reusable UI components
│   ├── ui/          # Generic primitives
│   └── forms/       # Form components
├── hooks/            # Custom hooks
├── lib/              # Utilities, clients, constants
│   ├── api/         # API clients
│   ├── utils/       # Helper functions
│   └── constants/   # Named constants
├── types/            # TypeScript types
└── styles/           # Global styles
```

### File Naming

```
components/Button.tsx        # PascalCase for components
hooks/useAuth.ts             # camelCase with 'use' prefix
lib/formatDate.ts            # camelCase for utilities
types/user.types.ts          # camelCase with .types suffix
```

## Comments & Documentation

```typescript
// GOOD: Explain WHY, not WHAT
// Exponential backoff to avoid overwhelming the API during outages
const delay = Math.min(1000 * Math.pow(2, retryCount), 30000)

// BAD: Stating the obvious
// Increment counter by 1
count++

// Set name to user's name
name = user.name
```

## Testing Standards

### AAA Pattern

```typescript
test('returns empty array when no items match query', () => {
  // Arrange
  const items: Item[] = []

  // Act
  const result = searchItems(items, 'query')

  // Assert
  expect(result).toEqual([])
})
```

### Test Naming

```typescript
// GOOD: Descriptive
test('throws error when API key is missing', () => { })
test('falls back to cache when network unavailable', () => { })

// BAD: Vague
test('works', () => { })
test('test search', () => { })
```

## Code Smell Detection

<quality-rules>
Watch for these anti-patterns:

### 1. Long Functions (> 50 lines)
Split into smaller, named functions with single responsibility.

### 2. Deep Nesting (5+ levels)
Use early returns to flatten:
```typescript
// BAD
if (user) { if (user.isAdmin) { if (resource) { /* ... */ } } }

// GOOD
if (!user) return
if (!user.isAdmin) return
if (!resource) return
// do something
```

### 3. Magic Numbers
```typescript
const MAX_RETRIES = 3          // GOOD
const DEBOUNCE_DELAY_MS = 500  // GOOD
if (retryCount > 3) { }        // BAD -- unexplained literal
```

### 4. God Objects
One class/file doing too much. Decompose into focused modules.

### 5. Premature Abstraction
Do not abstract until you have 3+ concrete examples of the same pattern.
</quality-rules>

**Code quality is not negotiable. Clear, maintainable code enables rapid development and confident refactoring.**
