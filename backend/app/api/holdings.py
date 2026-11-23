"""HTTP routes for ETF holdings."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.config import Settings, get_settings
from app.models.holding import HoldingCreate, HoldingResponse
from app.repositories.holdings import HoldingRepository

router = APIRouter(prefix="/holdings", tags=["holdings"])


def get_holding_repository(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HoldingRepository:
    """Build the repository using environment-based AWS configuration."""
    return HoldingRepository(
        table_name=settings.dynamodb_table_name,
        region_name=settings.aws_region,
        portfolio_id=settings.portfolio_id,
    )


RepositoryDependency = Annotated[
    HoldingRepository,
    Depends(get_holding_repository),
]


@router.post(
    "",
    response_model=HoldingResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_holding(
    holding: HoldingCreate,
    repository: RepositoryDependency,
) -> HoldingResponse:
    return repository.create(holding)


@router.get(
    "",
    response_model=list[HoldingResponse],
    response_model_exclude_none=True,
)
def list_holdings(repository: RepositoryDependency) -> list[HoldingResponse]:
    return repository.list()


@router.get(
    "/{holding_id}",
    response_model=HoldingResponse,
    response_model_exclude_none=True,
)
def get_holding(
    holding_id: UUID,
    repository: RepositoryDependency,
) -> HoldingResponse:
    holding = repository.get(str(holding_id))
    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    return holding


@router.put(
    "/{holding_id}",
    response_model=HoldingResponse,
    response_model_exclude_none=True,
)
def update_holding(
    holding_id: UUID,
    holding: HoldingCreate,
    repository: RepositoryDependency,
) -> HoldingResponse:
    updated_holding = repository.update(str(holding_id), holding)
    if updated_holding is None:
        raise HTTPException(status_code=404, detail="Holding not found")
    return updated_holding


@router.delete("/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holding(
    holding_id: UUID,
    repository: RepositoryDependency,
) -> Response:
    if not repository.delete(str(holding_id)):
        raise HTTPException(status_code=404, detail="Holding not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

