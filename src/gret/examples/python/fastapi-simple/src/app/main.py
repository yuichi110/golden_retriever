"""FastAPI application entrypoint and middleware setup."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import router

app = FastAPI(
    title="FastAPI Simple Service",
    description="Starter service conforming to Golden Retriever conventions.",
    version="0.1.0",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Standard error response envelope handler conforming to RFC 7807."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            }
        },
    )


app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint for container orchestrators."""
    return {"status": "ok"}
