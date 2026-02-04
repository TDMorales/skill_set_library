# Error Handling (Python)

## ❌ BROKEN EXAMPLE (DO NOT COPY)

Inconsistent error response shape and leaked internals, no request ID propagation.

~~~python
"""
What breaks
- Error responses do not follow the standard format
- No requestId is included for correlation
- Stack traces leak in production
- Operational errors are not represented as AppError types
"""

# =============================================================================
# BROKEN DIFF (DO NOT COPY)
# =============================================================================
# --- a/middleware/error_handler.py
# +++ b/middleware/error_handler.py
# @@
# - async def app_error_handler(request: Request, exc: AppError):
# -     return JSONResponse(
# -         status_code=exc.status_code,
# -         content={
# -             "error": {
# -                 "code": exc.code,
# -                 "message": exc.message,
# -                 "details": exc.details,
# -                 "requestId": request.headers.get("x-request-id"),
# -             }
# -         },
# -     )
# + @app.exception_handler(Exception)
# + async def unhandled_exception_handler(request, exc):
# +     return JSONResponse(
# +         status_code=500,
# +         content={"error": str(exc), "stack": repr(exc)},
# +     )
#   # ❌ BUG: unstructured response and internal details leaked
#
# --- a/routes/users.py
# +++ b/routes/users.py
# @@
# - if not user:
# -     raise NotFoundError("User", user_id)
# + if not user:
# +     raise HTTPException(status_code=404, detail="User not found")
#   # ❌ BUG: bypasses AppError and stable error codes
# =============================================================================
~~~

## CORRECT EXAMPLE

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
```

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
```

## EXPLICIT EXAMPLE (EDGE CASE)

```python
# Map validation errors to a stable code and consistent details
errors = [{"field": "email", "message": "Invalid format"}]
raise ValidationError(errors)
```
