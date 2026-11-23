"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(title="ETF Portfolio Dashboard API")


@app.get("/health")
def get_health() -> dict[str, str]:
    """Report whether the API process is running."""
    return {"status": "ok"}

