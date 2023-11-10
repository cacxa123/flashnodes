import random
import string
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.schemas import Project, ProjectDB, ProjectResponse

router = APIRouter()


@router.post("/request", response_model=ProjectResponse)
def create_project(
        body: Project,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user),
):
    crypto = crud.crypto.get_by_symbol(db, body.cryptocurrency_symbol)
    if not crypto:
        raise HTTPException(
            status_code=404,
            detail="Cryptocurrency with given symbol does not exist"
        )
    new_project = ProjectDB(
        user_id=current_user.id,
        cryptocurrency_symbol=body.cryptocurrency_symbol,
        mode=body.mode,
        network=body.network,
        pay_until=body.pay_until,
        prefix=''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    )
    project = crud.projects.create(db, new_project)
    # Data encapsulation
    return ProjectResponse(
        node_id=project.node_id,
        cryptocurrency_symbol=project.cryptocurrency_symbol,
        cryptocurrency_full_name=crypto.full_name,
        mode=project.mode.value,
        network=project.network.value,
        is_paid=project.is_paid,
        paid_until=str(project.paid_until) if project.paid_until else None,
        created_on=str(project.created_on),
        api_key=project.api_key,
        status=project.status,
        public_address=current_user.public_address,
        prefix=project.prefix
    )


@router.get("", status_code=200)
def get_projects(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)):
    return {
        "results": [
            ProjectResponse(
                node_id=project.node_id,
                cryptocurrency_symbol=project.cryptocurrency_symbol,
                cryptocurrency_full_name=cryptocurrency_full_name,
                mode=project.mode.value,
                network=project.network.value,
                is_paid=project.is_paid,
                paid_until=str(project.paid_until),
                created_on=str(project.created_on),
                api_key=project.api_key,
                status=project.status,
                public_address=current_user.public_address,
                prefix=project.prefix
            ) for project, cryptocurrency_full_name in crud.projects.get_all(db, current_user.id)
        ]
    }


@router.get("/{node_id}", status_code=200)
def get_project(
        node_id: UUID,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_user)
):
    project = crud.projects.get_by_node_id(db, node_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project does not exist"
        )
    project, cryptocurrency_full_name = project
    result = ProjectResponse(
        node_id=project.node_id,
        cryptocurrency_symbol=project.cryptocurrency_symbol,
        cryptocurrency_full_name=cryptocurrency_full_name,
        mode=project.mode.value,
        network=project.network.value,
        is_paid=project.is_paid,
        paid_until=str(project.paid_until),
        created_on=str(project.created_on),
        api_key=project.api_key,
        status=project.status,
        public_address=current_user.public_address,
        prefix=project.prefix
    )
    return {
        "result": result
    }


@router.get("/cryptocurrencies", status_code=200)
def get_cryptocurrencies(
        db: Session = Depends(deps.get_db),
        # current_user: models.User = Depends(deps.get_current_user)
):
    return {
        "results": crud.crypto.get_all(db)
    }
