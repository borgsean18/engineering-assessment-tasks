from datetime import date
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.enums import (
    BenchmarkPosition,
    ChangeOrderStatus,
    CreateChangeOrderStatus,
    ProjectStatus,
    RagStatus,
)

T = TypeVar("T")


class CamelModel(BaseModel):
    """Base model: snake_case fields, camelCase JSON (from FastAPI OpenAPI export)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True,
    )


class Project(CamelModel):
    """Summary representation of a portfolio project."""

    id: str
    name: str
    region: str
    sector: str
    status: ProjectStatus
    start_date: date
    planned_end_date: date
    baseline_cost: float
    currency: str


class ProjectDetail(Project):
    """Extended project view with computed cost and schedule KPIs."""

    actual_cost_to_date: float
    cost_variance: float
    schedule_slippage_days: int
    open_change_order_count: int


class CostSnapshot(CamelModel):
    """A single month's baseline, forecast, and actual cost figures."""

    period_month: date
    work_package_id: str | None = None
    baseline_cost: float
    forecast_cost: float
    actual_cost: float


class Milestone(CamelModel):
    """A schedule milestone with dates and RAG status."""

    id: str
    name: str
    planned_date: date
    forecast_date: date | None = None
    actual_date: date | None = None
    rag_status: RagStatus


class ChangeOrder(CamelModel):
    """A change order with cost and schedule impact."""

    id: str
    work_package_id: str | None = None
    work_package_code: str | None = None
    reference: str
    title: str
    status: ChangeOrderStatus
    cost_delta: float
    schedule_delta_days: int
    raised_date: date


class ChangeOrderCreate(CamelModel):
    """Request body for creating a new change order."""

    reference: str = Field(min_length=1)
    title: str = Field(min_length=1)
    cost_delta: float = Field(gt=0)
    schedule_delta_days: int = Field(gt=0)
    status: CreateChangeOrderStatus = CreateChangeOrderStatus.DRAFT
    raised_date: date | None = None
    work_package_code: str | None = None

class PaginatedResponse(CamelModel, Generic[T]):
    """Paginated list wrapper with total count and paging metadata."""

    items: list[T]
    total: int
    limit: int
    offset: int


class ChangeOrderList(PaginatedResponse[ChangeOrder]):
    """Paginated change order list."""


class BenchmarkComparison(CamelModel):
    """A project's unit-cost metric compared against sector/region peer distribution."""

    metric_key: str
    unit: str
    project_value: float
    peer_median: float
    peer_p25: float
    peer_p75: float
    position: BenchmarkPosition


class ErrorResponse(CamelModel):
    """Standard error response body."""

    detail: str
