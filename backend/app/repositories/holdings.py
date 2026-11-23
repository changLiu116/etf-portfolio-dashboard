"""DynamoDB persistence for ETF holdings."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Key

from app.models.holding import HoldingCreate, HoldingResponse


class HoldingRepository:
    """Store and retrieve holdings from a DynamoDB table."""

    def __init__(
        self,
        table_name: str,
        region_name: str,
        portfolio_id: str,
    ) -> None:
        self._table = boto3.resource(
            "dynamodb",
            region_name=region_name,
        ).Table(table_name)
        self._partition_key = f"PORTFOLIO#{portfolio_id}"

    def create(self, holding: HoldingCreate) -> HoldingResponse:
        holding_id = str(uuid4())
        timestamp = datetime.now(UTC)
        response = HoldingResponse(
            **holding.model_dump(),
            holding_id=holding_id,
            created_at=timestamp,
            updated_at=timestamp,
        )

        self._table.put_item(Item=self._to_item(response))
        return response

    def list(self) -> list[HoldingResponse]:
        response = self._table.query(
            KeyConditionExpression=(
                Key("PK").eq(self._partition_key)
                & Key("SK").begins_with("HOLDING#")
            ),
            ConsistentRead=True,
        )
        return [self._from_item(item) for item in response.get("Items", [])]

    def get(self, holding_id: str) -> HoldingResponse | None:
        response = self._table.get_item(
            Key=self._key(holding_id),
            ConsistentRead=True,
        )
        item = response.get("Item")
        return self._from_item(item) if item else None

    def update(
        self,
        holding_id: str,
        holding: HoldingCreate,
    ) -> HoldingResponse | None:
        existing = self.get(holding_id)
        if existing is None:
            return None

        updated = HoldingResponse(
            **holding.model_dump(),
            holding_id=holding_id,
            created_at=existing.created_at,
            updated_at=datetime.now(UTC),
        )
        self._table.put_item(Item=self._to_item(updated))
        return updated

    def delete(self, holding_id: str) -> bool:
        response = self._table.delete_item(
            Key=self._key(holding_id),
            ReturnValues="ALL_OLD",
        )
        return "Attributes" in response

    def _key(self, holding_id: str) -> dict[str, str]:
        return {
            "PK": self._partition_key,
            "SK": f"HOLDING#{holding_id}",
        }

    def _to_item(self, holding: HoldingResponse) -> dict[str, Any]:
        holding_data = holding.model_dump(exclude_none=True)
        holding_data["created_at"] = holding.created_at.isoformat()
        holding_data["updated_at"] = holding.updated_at.isoformat()
        item = {
            **self._key(holding.holding_id),
            "entity_type": "holding",
            **holding_data,
        }
        return item

    @staticmethod
    def _from_item(item: dict[str, Any]) -> HoldingResponse:
        application_fields = {
            key: value
            for key, value in item.items()
            if key not in {"PK", "SK", "entity_type"}
        }
        return HoldingResponse.model_validate(application_fields)

