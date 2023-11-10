from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic.types import UUID
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.prometheus import get_analytics, get_analytics_total
from app.utils import generate_timestamp_list, collapse_prometheus_response, literal_to_seconds

router = APIRouter()


@router.get("/total", status_code=200)
def get_project_analytics_total(
        timerange: Literal["1h", "1d", "7d", "30d"],
        db: Session = Depends(deps.get_db),
        steps: int = 6,
        current_user: models.User = Depends(deps.get_current_user)
):
    if not 1 < steps < 100:
        raise HTTPException(
            status_code=422,
            detail="Step should be bigger than 1 and smaller than 100"
        )
    api_key_projects = [str(project.api_key) for project in crud.projects.get_all_api_keys(db, current_user.id)]
    if not api_key_projects:
        raise HTTPException(
            status_code=404,
            detail="No projects found"
        )

    analytics = get_analytics_total(api_key_projects, timerange)
    if analytics:
        values = [step["value"] for step in analytics]
        total = sum(values)
        return {
            "chart": analytics,
            "total": total,
            "average": round(total/literal_to_seconds(timerange), 2)
        }
    hours = 0
    if timerange == "1h":
        hours += 1
    else:
        hours += int(timerange[:-1])*24
    timestamp_list = [{
            "timestamp": timestamp,
            "value": 0
        } for timestamp in generate_timestamp_list(hours=hours)]  # replace method later
    return {
        "chart": collapse_prometheus_response(timestamp_list, steps),
        "total": 0,
        "average": 0
    }


@router.get("/{node_id}", status_code=200)
def get_project_analytics(
        node_id: UUID,
        timerange: Literal["1h", "1d", "7d", "30d"],
        steps: int = 6,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    if not 1 < steps < 100:
        raise HTTPException(
            status_code=422,
            detail="Step should be bigger than 1 and smaller than 100"
        )
    api_key_project = crud.projects.get_api_key_by_node_id(db, current_user.id, node_id)
    if not api_key_project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    analytics = get_analytics(api_key_project.api_key, timerange)
    if analytics:
        values = [step["value"] for step in analytics]
        total = sum(values)
        return {
            "chart": analytics,
            "total": total,
            "average": round(total/literal_to_seconds(timerange), 2)
        }
    hours = 0
    if timerange == "1h":
        hours += 1
    else:
        hours += int(timerange[0]) * 24
    hours = 0
    if timerange == "1h":
        hours += 1
    else:
        hours += int(timerange[:-1]) * 24
    timestamp_list = [{
        "timestamp": timestamp,
        "value": 0
    } for timestamp in generate_timestamp_list(hours=hours)]  # replace method later
    return {
        "chart": collapse_prometheus_response(timestamp_list, steps),
        "total": 0,
        "average": 0
    }
