"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.holdings import router as holdings_router

app = FastAPI(title="ETF Portfolio Dashboard API")
app.include_router(holdings_router)


@app.get("/health")
def get_health() -> dict[str, str]:
    """Report whether the API process is running."""
    return {"status": "ok"}

