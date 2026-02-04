---
name: error-handling
description: Implement consistent error handling with custom error classes, error boundaries, and structured error responses. Covers logging, monitoring, and user-friendly messages.
license: MIT
compatibility: TypeScript/JavaScript, Python
category: api
time: 3h
source: drift-masterguide
---

# Error Handling

Handle errors gracefully and consistently across your application.

---

## 1. Purpose

Implement a reliable, structured error handling system that:
- Uses custom error classes and stable error codes
- Returns consistent API error responses
- Logs operational vs programming errors appropriately
- Avoids leaking internal details in production
- Enables client-side error handling and user-friendly messages

---

## 2. When to Use

Apply this skill when any of the following are true:
- You return API error responses
- You handle database or validation errors
- You integrate with external services
- You need consistent error formatting across services
- You want safer client-side error handling

---

## 3. Error Response Format

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User not found",
    "details": { "userId": "123" },
    "requestId": "req_abc123"
  }
}
```

---

## 4. Definitions

- **Error Code**: Stable, machine-readable identifier (e.g., `VALIDATION_ERROR`).
- **Operational Error**: Expected failure that is safe to report to clients.
- **Programming Error**: Unexpected failure (bugs, unhandled cases) that should not leak details.
- **Error Boundary**: A centralized handler that formats, logs, and responds to errors.
- **Request ID**: A trace identifier that links logs to API responses.

---

## 5. Hard Invariants

The following invariants are mandatory and non-negotiable:

1. **Structured Error Response**
   - All API error responses MUST follow the standard response format.
   - The `error.code` field MUST be present and stable.

2. **Custom Error Types**
   - Application-level errors MUST be expressed via custom error classes.
   - Each custom error MUST include a status code and error code.

3. **Request ID Propagation**
   - If a request ID is present, it MUST be included in error responses and logs.

4. **Operational vs Programming Errors**
   - Operational errors MUST be logged at warn level and returned with their status code.
   - Programming errors MUST be logged at error level and return a safe 500 response.

5. **No Internal Leakage**
   - Stack traces and internal error details MUST NOT be returned in production.

6. **Consistent Client Handling**
   - Frontend or client code MUST rely on error codes, not string matching.

---

## 6. Procedure

Follow these steps in order:

1. Define custom error classes with code, message, status, and optional details.
2. Implement a centralized error handler (API boundary or middleware).
3. Map known library errors (e.g., database errors) to consistent responses.
4. Log operational errors with context and request ID.
5. Log programming errors with stack trace and request ID.
6. Ensure production responses do not leak internal details.
7. Implement client-side error handling using error codes.

---

## Audit Mode (Repo Scanning Procedure)

Use Audit Mode when asked to scan a repo and identify violations of error-handling rules.

The assistant **must** follow this exact sequence:

1. **Identify error surfaces**
   - API handlers, middleware, background jobs, and client error layers.
2. **Trace response formatting**
   - Confirm all error responses follow the standard format.
3. **Check error types**
   - Locate custom error classes and their usage.
4. **Inspect logging behavior**
   - Distinguish operational vs programming errors.
5. **Check invariants**
   - Evaluate EH-* items against code evidence.
6. **Produce findings using the required schema**
   - Every violation or missing requirement MUST be reported as a finding.
7. **Propose minimal fixes**
   - Prefer scoped changes over rewrites.

Audit Mode **must not** end without:
- at least one pass over an error path
- a completed findings list (even if empty)

---

## 7. Validation Checklist

All items below MUST pass:

- [ ] API error responses follow the standard structure
- [ ] Error codes are stable and machine-readable
- [ ] Custom error types exist for operational errors
- [ ] Request ID is included in error responses when present
- [ ] Operational errors are logged at warn level
- [ ] Programming errors are logged at error level
- [ ] No stack traces or internals leak in production
- [ ] Clients handle errors via error codes

Failure of any item blocks completion.

---

## 8. Output Contract

When this skill is executed, the agent MUST produce:

- Custom error classes (TypeScript or Python)
- A centralized error handler (middleware or exception handler)
- Structured error responses matching the format
- Client-side handling that uses error codes
- A short summary describing:
  - Error codes used
  - Error boundary location
  - Logging behavior

---

## 9. TypeScript Implementation Reference

### Custom Error Classes

```typescript
// errors/app-error.ts
export class AppError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number = 500,
    public details?: Record<string, unknown>,
    public isOperational: boolean = true
  ) {
    super(message);
    this.name = 'AppError';
    Error.captureStackTrace(this, this.constructor);
  }
}

// Common error types
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

export class ValidationError extends AppError {
  constructor(details: Array<{ field: string; message: string }>) {
    super('VALIDATION_ERROR', 'Validation failed', 400, { errors: details });
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Authentication required') {
    super('UNAUTHORIZED', message, 401);
  }
}

export class ForbiddenError extends AppError {
  constructor(message = 'Access denied') {
    super('FORBIDDEN', message, 403);
  }
}

export class ConflictError extends AppError {
  constructor(message: string, details?: Record<string, unknown>) {
    super('CONFLICT', message, 409, details);
  }
}

export class RateLimitError extends AppError {
  constructor(retryAfter: number) {
    super('RATE_LIMITED', 'Too many requests', 429, { retryAfter });
  }
}

export class ExternalServiceError extends AppError {
  constructor(service: string, originalError?: Error) {
    super(
      'EXTERNAL_SERVICE_ERROR',
      `${service} service unavailable`,
      503,
      { service, originalMessage: originalError?.message }
    );
  }
}
```

### Error Handler Middleware

```typescript
// middleware/error-handler.ts
import { Request, Response, NextFunction } from 'express';
import { AppError } from '../errors/app-error';
import { logger } from '../utils/logger';

interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    requestId?: string;
  };
}

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  const requestId = req.headers['x-request-id'] as string;

  // Handle known operational errors
  if (err instanceof AppError) {
    logger.warn('Operational error', {
      code: err.code,
      message: err.message,
      statusCode: err.statusCode,
      requestId,
      path: req.path,
    });

    const response: ErrorResponse = {
      error: {
        code: err.code,
        message: err.message,
        details: err.details,
        requestId,
      },
    };

    return res.status(err.statusCode).json(response);
  }

  // Handle Prisma errors
  if (err.name === 'PrismaClientKnownRequestError') {
    const prismaError = err as any;
    if (prismaError.code === 'P2002') {
      return res.status(409).json({
        error: {
          code: 'DUPLICATE_ENTRY',
          message: 'Resource already exists',
          details: { fields: prismaError.meta?.target },
          requestId,
        },
      });
    }
    if (prismaError.code === 'P2025') {
      return res.status(404).json({
        error: {
          code: 'RESOURCE_NOT_FOUND',
          message: 'Resource not found',
          requestId,
        },
      });
    }
  }

  // Handle unknown errors (programming errors)
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    requestId,
    path: req.path,
  });

  // Do not leak error details in production
  const message = process.env.NODE_ENV === 'production'
    ? 'Internal server error'
    : err.message;

  return res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message,
      requestId,
    },
  });
}
```

### Async Handler Wrapper

```typescript
// utils/async-handler.ts
import { Request, Response, NextFunction, RequestHandler } from 'express';

type AsyncRequestHandler = (
  req: Request,
  res: Response,
  next: NextFunction
) => Promise<any>;

export function asyncHandler(fn: AsyncRequestHandler): RequestHandler {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}
```

### Service Layer Error Handling

```typescript
// services/user-service.ts
import { NotFoundError, ConflictError } from '../errors/app-error';

class UserService {
  async findById(id: string): Promise<User> {
    const user = await db.users.findUnique({ where: { id } });
    if (!user) {
      throw new NotFoundError('User', id);
    }
    return user;
  }

  async create(data: CreateUserInput): Promise<User> {
    const existing = await db.users.findUnique({ where: { email: data.email } });
    if (existing) {
      throw new ConflictError('Email already registered', { email: data.email });
    }
    return db.users.create({ data });
  }

  async updateEmail(userId: string, newEmail: string): Promise<User> {
    try {
      return await db.users.update({
        where: { id: userId },
        data: { email: newEmail },
      });
    } catch (error: any) {
      if (error.code === 'P2002') {
        throw new ConflictError('Email already in use');
      }
      throw error;
    }
  }
}
```

---

## 10. Python Implementation Reference

```python
# errors/app_error.py
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class AppError(Exception):
    code: str
    message: str
    status_code: int = 500
    details: Optional[dict[str, Any]] = None

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str = None):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} not found",
            status_code=404,
            details={f"{resource.lower()}_id": id} if id else None,
        )

class ValidationError(AppError):
    def __init__(self, errors: list[dict]):
        super().__init__(
            code="VALIDATION_ERROR",
            message="Validation failed",
            status_code=400,
            details={"errors": errors},
        )

class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)

class ForbiddenError(AppError):
    def __init__(self, message: str = "Access denied"):
        super().__init__(code="FORBIDDEN", message=message, status_code=403)
```

### FastAPI Error Handler

```python
# middleware/error_handler.py
from fastapi import Request
from fastapi.responses import JSONResponse
from errors.app_error import AppError

async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "requestId": request.headers.get("x-request-id"),
            }
        },
    )

# Register in app
app.add_exception_handler(AppError, app_error_handler)
```

---

## 11. Frontend Error Handling Reference

```typescript
// api-client.ts
class ApiError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number,
    public details?: Record<string, unknown>
  ) {
    super(message);
  }
}

async function apiRequest<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);

  if (!response.ok) {
    const body = await response.json();
    throw new ApiError(
      body.error.code,
      body.error.message,
      response.status,
      body.error.details
    );
  }

  return response.json();
}

// Usage with error handling
try {
  const user = await apiRequest('/api/users/123');
} catch (error) {
  if (error instanceof ApiError) {
    if (error.code === 'RESOURCE_NOT_FOUND') {
      showNotification('User not found');
    } else if (error.code === 'VALIDATION_ERROR') {
      showFormErrors(error.details.errors);
    }
  }
}
```

---

## 12. Best Practices

1. Use stable error codes.
2. Always include a request ID when available.
3. Log operational errors at warn level.
4. Log unexpected errors at error level with stack traces.
5. Never expose internals in production responses.
6. Keep client-side handling code driven by error codes.

---

## 13. Common Mistakes

- Returning stack traces to users
- Generic "Something went wrong" without a code
- Not logging errors
- Inconsistent error formats across services
- Swallowing exceptions and returning success

---

## Required Output Schema (Audit Findings)

When in Audit Mode, output **must** follow this format:

### Assumptions
- target language:
- constraints:
- scope (paths reviewed):

### Findings
For each finding, include:

- **ID:** `EH-###`
- **Severity:** `critical | high | medium | low`
- **Rule:** (one of EH-* invariants)
- **Location:** `path/to/file.ext:Lx-Ly`
- **Evidence:** short excerpt (1-8 lines)
- **Impact:** what breaks or becomes harder to change
- **Minimal Fix:** concrete change (describe or patch snippet)
- **Confidence:** `high | medium | low`

If there are no violations, output:
- **Findings:** `none`

### Validation Checklist Summary
- A copy of the checklist with each item marked:
  - `[x]` verified
  - `[ ]` not verified / missing
  - `[!]` violated (must link to finding IDs)

---

## Refusal Conditions

- Requests to expose stack traces or internal details in production responses
- Requests to bypass structured error responses
- Requests that require file access outside the repository scope
