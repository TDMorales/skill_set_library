# Error Handling (TypeScript)

## ❌ BROKEN EXAMPLE (DO NOT COPY)

Inconsistent error response shape, no stable codes, and stack traces are exposed.

~~~typescript
/**
 * What breaks
 * - Error responses do not follow the standard format
 * - Missing error codes for client handling
 * - Request ID is not propagated
 * - Stack traces leak to clients
 */

// =============================================================================
// BROKEN DIFF (DO NOT COPY)
// =============================================================================
// --- a/middleware/error-handler.ts
// +++ b/middleware/error-handler.ts
// @@
// - if (err instanceof AppError) {
// -   return res.status(err.statusCode).json({
// -     error: { code: err.code, message: err.message, requestId },
// -   });
// - }
// - return res.status(500).json({
// -   error: { code: 'INTERNAL_ERROR', message: 'Internal server error', requestId },
// - });
// + return res.status(500).json({
// +   error: err.message,
// +   stack: err.stack,
// + });
//   // ❌ BUG: unstructured response and internal details leaked
//
// --- a/routes/users.ts
// +++ b/routes/users.ts
// @@
// - if (!user) throw new NotFoundError('User', req.params.id);
// + if (!user) return res.status(404).json({ message: 'User not found' });
//   // ❌ BUG: bypasses AppError and stable error codes
// =============================================================================
~~~

## CORRECT EXAMPLE

```typescript
// errors/app-error.ts
export class AppError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number = 500,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'AppError';
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id?: string) {
    super(
      'RESOURCE_NOT_FOUND',
      `${resource} not found`,
      404,
      id ? { [`${resource.toLowerCase()}Id`]: id } : undefined
    );
  }
}
```

```typescript
// middleware/error-handler.ts
import { AppError } from '../errors/app-error';
import { logger } from '../utils/logger';

export function errorHandler(err, req, res, next) {
  const requestId = req.headers['x-request-id'];

  if (err instanceof AppError) {
    logger.warn('Operational error', { code: err.code, requestId });
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        details: err.details,
        requestId,
      },
    });
  }

  logger.error('Unhandled error', { error: err.message, requestId });
  return res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'Internal server error',
      requestId,
    },
  });
}
```

## EXPLICIT EXAMPLE (EDGE CASE)

```typescript
// External service failure mapped to a stable code
try {
  const result = await payments.charge();
  return res.json(result);
} catch (err) {
  throw new ExternalServiceError('payments', err as Error);
}
```
