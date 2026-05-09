---
name: backend-patterns
description: "Backend architecture patterns for scalable server-side applications: API design, repository pattern, service layer, database optimization, caching, error handling, JWT auth, RBAC, rate limiting, and structured logging. Derived from Everything Claude Code (https://github.com/affaan-m/everything-claude-code)."
---

# Backend Development Patterns

Backend architecture patterns and best practices for scalable server-side applications.

## When to Activate

- Designing REST or GraphQL API endpoints
- Implementing repository, service, or controller layers
- Optimizing database queries (N+1, indexing, connection pooling)
- Adding caching (Redis, in-memory, HTTP cache headers)
- Setting up background jobs or async processing
- Structuring error handling and validation for APIs
- Building middleware (auth, logging, rate limiting)

## API Design Patterns

### Repository Pattern

```typescript
// Abstract data access logic behind an interface
interface ItemRepository {
  findAll(filters?: ItemFilters): Promise<Item[]>
  findById(id: string): Promise<Item | null>
  create(data: CreateItemDto): Promise<Item>
  update(id: string, data: UpdateItemDto): Promise<Item>
  delete(id: string): Promise<void>
}

class DatabaseItemRepository implements ItemRepository {
  async findAll(filters?: ItemFilters): Promise<Item[]> {
    let query = db.from('items').select('id, name, status, created_at')

    if (filters?.status) query = query.where('status', filters.status)
    if (filters?.limit) query = query.limit(filters.limit)

    return await query
  }
}
```

### Service Layer Pattern

```typescript
// Separate business logic from data access
class ItemService {
  constructor(private itemRepo: ItemRepository) {}

  async search(query: string, limit = 10): Promise<Item[]> {
    const results = await this.itemRepo.findAll({ query, limit })
    return results.sort((a, b) => b.relevanceScore - a.relevanceScore)
  }
}
```

### Middleware Pattern

```typescript
export function withAuth(handler: NextApiHandler): NextApiHandler {
  return async (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '')

    if (!token) return res.status(401).json({ error: 'Unauthorized' })

    try {
      const user = await verifyToken(token)
      req.user = user
      return handler(req, res)
    } catch {
      return res.status(401).json({ error: 'Invalid token' })
    }
  }
}
```

## Database Patterns

### Query Optimization

```typescript
// GOOD: Select only needed columns
const items = await db.from('items')
  .select('id, name, status')
  .where('status', 'active')
  .orderBy('created_at', 'desc')
  .limit(10)

// BAD: Select everything
const items = await db.from('items').select('*')
```

### N+1 Query Prevention

```typescript
// BAD: N+1 query problem
const items = await getItems()
for (const item of items) {
  item.owner = await getUser(item.owner_id)  // N queries!
}

// GOOD: Batch fetch
const items = await getItems()
const ownerIds = items.map(i => i.owner_id)
const owners = await getUsers(ownerIds)  // 1 query
const ownerMap = new Map(owners.map(o => [o.id, o]))
items.forEach(item => { item.owner = ownerMap.get(item.owner_id) })
```

### Transaction Pattern

```typescript
async function createItemWithAudit(itemData: CreateItemDto, userId: string) {
  return await db.transaction(async (trx) => {
    const item = await trx('items').insert(itemData).returning('*')
    await trx('audit_log').insert({ action: 'create', resource: 'item', user_id: userId })
    return item[0]
  })
}
```

## Caching Strategies

### Cache-Aside Pattern

```typescript
async function getItemWithCache(id: string): Promise<Item> {
  const cacheKey = `item:${id}`

  const cached = await redis.get(cacheKey)
  if (cached) return JSON.parse(cached)

  const item = await db.items.findUnique({ where: { id } })
  if (!item) throw new ApiError(404, 'Item not found')

  await redis.setex(cacheKey, 300, JSON.stringify(item))  // TTL: 5 minutes
  return item
}

async function invalidateItemCache(id: string) {
  await redis.del(`item:${id}`)
}
```

## Error Handling Patterns

### Centralized Error Handler

```typescript
class ApiError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational = true
  ) {
    super(message)
    Object.setPrototypeOf(this, ApiError.prototype)
  }
}

export function errorHandler(error: unknown): Response {
  if (error instanceof ApiError) {
    return NextResponse.json({ error: error.message }, { status: error.statusCode })
  }

  if (error instanceof z.ZodError) {
    return NextResponse.json({
      error: 'Validation failed',
      details: error.errors,
    }, { status: 400 })
  }

  console.error('Unexpected error:', error)
  return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
}
```

### Retry with Exponential Backoff

```typescript
async function fetchWithRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  let lastError: Error

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      lastError = error as Error
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000))
      }
    }
  }

  throw lastError!
}
```

## Authentication & Authorization

### JWT Token Validation

```typescript
interface JWTPayload { userId: string; email: string; role: 'admin' | 'user' }

export function verifyToken(token: string): JWTPayload {
  try {
    return jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload
  } catch {
    throw new ApiError(401, 'Invalid token')
  }
}

export async function requireAuth(request: Request) {
  const token = request.headers.get('authorization')?.replace('Bearer ', '')
  if (!token) throw new ApiError(401, 'Missing authorization token')
  return verifyToken(token)
}
```

### Role-Based Access Control (RBAC)

```typescript
type Permission = 'read' | 'write' | 'delete' | 'admin'
type Role = 'admin' | 'moderator' | 'user'

const rolePermissions: Record<Role, Permission[]> = {
  admin: ['read', 'write', 'delete', 'admin'],
  moderator: ['read', 'write', 'delete'],
  user: ['read', 'write'],
}

export function hasPermission(role: Role, permission: Permission): boolean {
  return rolePermissions[role].includes(permission)
}

export function requirePermission(permission: Permission) {
  return (handler: Function) => async (request: Request) => {
    const user = await requireAuth(request)
    if (!hasPermission(user.role, permission)) {
      throw new ApiError(403, 'Insufficient permissions')
    }
    return handler(request, user)
  }
}
```

## Rate Limiting

```typescript
class RateLimiter {
  private requests = new Map<string, number[]>()

  isAllowed(identifier: string, maxRequests: number, windowMs: number): boolean {
    const now = Date.now()
    const recentRequests = (this.requests.get(identifier) || [])
      .filter(time => now - time < windowMs)

    if (recentRequests.length >= maxRequests) return false

    recentRequests.push(now)
    this.requests.set(identifier, recentRequests)
    return true
  }
}

const limiter = new RateLimiter()

export async function GET(request: Request) {
  const ip = request.headers.get('x-forwarded-for') || 'unknown'

  if (!limiter.isAllowed(ip, 100, 60000)) {
    return NextResponse.json({ error: 'Rate limit exceeded' }, { status: 429 })
  }

  // Continue with request
}
```

## Structured Logging

```typescript
interface LogContext { userId?: string; requestId?: string; [key: string]: unknown }

class Logger {
  log(level: 'info' | 'warn' | 'error', message: string, context?: LogContext) {
    console.log(JSON.stringify({ timestamp: new Date().toISOString(), level, message, ...context }))
  }

  info(message: string, context?: LogContext) { this.log('info', message, context) }
  warn(message: string, context?: LogContext) { this.log('warn', message, context) }
  error(message: string, error: Error, context?: LogContext) {
    this.log('error', message, { ...context, error: error.message, stack: error.stack })
  }
}

export const logger = new Logger()
```

**Backend patterns enable scalable, maintainable server-side applications. Choose patterns that fit your complexity level.**
