"""Unit tests for DynamoDB holding serialization."""

from decimal import Decimal
from unittest.mock import Mock, patch

from app.models.holding import HoldingCreate
from app.repositories.holdings import HoldingRepository


def test_create_omits_private_fields_and_preserves_decimal_numbers() -> None:
    table = Mock()
    dynamodb = Mock()
    dynamodb.Table.return_value = table

    with patch(
        "app.repositories.holdings.boto3.resource",
        return_value=dynamodb,
    ):
        repository = HoldingRepository(
            table_name="test-table",
            region_name="ca-central-1",
            portfolio_id="default",
        )

    created = repository.create(
        HoldingCreate(
            ticker="xgro",
            exchange="tsx",
            currency="CAD",
            average_cost=Decimal("27.42"),
        )
    )

    item = table.put_item.call_args.kwargs["Item"]
    assert item["PK"] == "PORTFOLIO#default"
    assert item["SK"] == f"HOLDING#{created.holding_id}"
    assert item["average_cost"] == Decimal("27.42")
    assert "quantity" not in item
    assert "account" not in item

