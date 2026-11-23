"""Environment-based application configuration."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    """Configuration values used by the API."""

    aws_region: str
    dynamodb_table_name: str
    portfolio_id: str


@lru_cache
def get_settings() -> Settings:
    """Read settings once per application process."""
    return Settings(
        aws_region=os.getenv("AWS_REGION", "us-east-2"),
        dynamodb_table_name=os.getenv(
            "DYNAMODB_TABLE_NAME",
            "etf-portfolio-dashboard-dev",
        ),
        portfolio_id=os.getenv("PORTFOLIO_ID", "default"),
    )

