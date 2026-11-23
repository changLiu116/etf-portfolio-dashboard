"""API tests for ETF holdings."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.holdings import get_holding_repository
from app.main import app
from app.models.holding import HoldingCreate, HoldingResponse


class InMemoryHoldingRepository:
    """Small repository fake that keeps API tests independent of AWS."""

    def __init__(self) -> None:
        self.holdings: dict[str, HoldingResponse] = {}

    def create(self, holding: HoldingCreate) -> HoldingResponse:
        holding_id = str(uuid4())
        timestamp = datetime.now(UTC)
        response = HoldingResponse(
            **holding.model_dump(),
            holding_id=holding_id,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self.holdings[holding_id] = response
        return response

    def list(self) -> list[HoldingResponse]:
        return list(self.holdings.values())

    def get(self, holding_id: str) -> HoldingResponse | None:
        return self.holdings.get(holding_id)

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
        self.holdings[holding_id] = updated
        return updated

    def delete(self, holding_id: str) -> bool:
        return self.holdings.pop(holding_id, None) is not None


@pytest.fixture
def client() -> TestClient:
    repository = InMemoryHoldingRepository()
    app.dependency_overrides[get_holding_repository] = lambda: repository

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_holding_crud_without_private_position_fields(client: TestClient) -> None:
    create_response = client.post(
        "/holdings",
        json={
            "ticker": " xgro ",
            "exchange": "tsx",
            "currency": "CAD",
            "average_cost": "27.42",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    holding_id = created["holding_id"]
    assert created["ticker"] == "XGRO"
    assert created["exchange"] == "TSX"
    assert created["average_cost"] == "27.42"
    assert "quantity" not in created
    assert "account" not in created

    list_response = client.get("/holdings")
    assert list_response.status_code == 200
    assert list_response.json() == [created]

    get_response = client.get(f"/holdings/{holding_id}")
    assert get_response.status_code == 200
    assert get_response.json() == created

    update_response = client.put(
        f"/holdings/{holding_id}",
        json={
            "ticker": "XGRO",
            "exchange": "TSX",
            "currency": "CAD",
            "average_cost": "28.10",
            "quantity": "5.5",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["quantity"] == "5.5"
    assert update_response.json()["average_cost"] == "28.10"

    delete_response = client.delete(f"/holdings/{holding_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/holdings/{holding_id}").status_code == 404


def test_rejects_non_positive_quantity(client: TestClient) -> None:
    response = client.post(
        "/holdings",
        json={
            "ticker": "XGRO",
            "exchange": "TSX",
            "currency": "CAD",
            "quantity": "0",
        },
    )

    assert response.status_code == 422


def test_missing_holding_returns_not_found(client: TestClient) -> None:
    missing_id = str(uuid4())

    assert client.get(f"/holdings/{missing_id}").status_code == 404
    assert (
        client.put(
            f"/holdings/{missing_id}",
            json={
                "ticker": "VFV",
                "exchange": "TSX",
                "currency": "CAD",
            },
        ).status_code
        == 404
    )
    assert client.delete(f"/holdings/{missing_id}").status_code == 404
