import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.db.models import ChangeOrder, Project, WorkPackage
from app.enums import ChangeOrderStatus
from app.routers.deps import get_project_or_404
from app.schemas import ChangeOrder as ChangeOrderSchema
from app.schemas import ChangeOrderCreate, ErrorResponse

router = APIRouter(prefix="/projects", tags=["change-orders"])


@router.get(
    "/{project_id}/change-orders",
    response_model=list[ChangeOrderSchema],
    operation_id="listChangeOrders",
)
def list_change_orders(
    project: Annotated[Project, Depends(get_project_or_404)],
    db: Annotated[Session, Depends(get_db)],
    status: Annotated[ChangeOrderStatus | None, Query()] = None,
) -> list[ChangeOrder]:
    """Return change orders for a project, optionally filtered by status."""
    stmt = select(ChangeOrder).where(ChangeOrder.project_id == project.id)
    if status:
        stmt = stmt.where(ChangeOrder.status == status)
    return list(db.scalars(stmt.order_by(ChangeOrder.raised_date)))

@router.post(
    "/{project_id}/change-orders",
    response_model=ChangeOrderSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id="createChangeOrder",
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse, "description": "Project not found"},
        status.HTTP_409_CONFLICT: {
            "model": ErrorResponse,
            "description": "Reference already used on this project",
        },
    },
)
def create_change_order(
    project: Annotated[Project, Depends(get_project_or_404)],
    db: Annotated[Session, Depends(get_db)],
    payload: ChangeOrderCreate,
) -> ChangeOrder:
    """Raise a new change order against a project."""
    dupplicate = db.scalar(
        select(ChangeOrder.id).where(
            ChangeOrder.project_id == project.id,
            ChangeOrder.reference == payload.reference,
        )
    )
    if dupplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{payload.reference} already exists on this project."
        )

    work_package_id:str | None = None
    if payload.work_package_code is not None:
        work_package_id = db.scalar(
            select(WorkPackage.id).where(
                WorkPackage.project_id == project.id,
                WorkPackage.code == payload.work_package_code,
            )
        )
        if work_package_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"{payload.work_package_code} does not belong to this project"
                )
            )

    change_order = ChangeOrder(
        id = str(uuid.uuid4()),
        project_id=project.id,
        work_package_id=work_package_id,
        referenc=payload.reference,
        title=payload.title,
        status=payload.status,
        cost_delta=payload.cost_delta,
        schedule_delta_days=payload.schedule_delta_days,
        raised_date=payload.raised_date or date.today(),
    )
    db.add(change_order)
    db.commit()
    db.refresh()
    return change_order
