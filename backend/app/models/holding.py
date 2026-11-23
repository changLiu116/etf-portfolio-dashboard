"""Data models for ETF holdings."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

PositiveDecimal = Annotated[Decimal, Field(gt=0)]
NonNegativeDecimal = Annotated[Decimal, Field(ge=0)]


class HoldingCreate(BaseModel):
    """Fields accepted when creating or replacing a holding."""

    model_config = ConfigDict(str_strip_whitespace=True)

    ticker: str = Field(min_length=1, max_length=20)
    exchange: str = Field(min_length=1, max_length=20)
    currency: Literal["CAD", "USD"]
    account: str | None = Field(default=None, min_length=1, max_length=100)
    quantity: PositiveDecimal | None = None
    average_cost: NonNegativeDecimal | None = None

    @field_validator("ticker", "exchange", mode="after")
    @classmethod
    def uppercase_identifier(cls, value: str) -> str:
        return value.upper()


class HoldingResponse(HoldingCreate):
    """Holding data returned by the API."""

    holding_id: str
    created_at: datetime
    updated_at: datetime

