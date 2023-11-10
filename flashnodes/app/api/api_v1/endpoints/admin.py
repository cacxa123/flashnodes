import random
import string
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.schemas import Cryptocurrency, ProjectResponse, Project, ProjectDB

router = APIRouter()


# Cryptocurrencies CRUD
@router.post("/cryptocurrencies", status_code=201)
def create_cryptocurrency(
        body: schemas.Cryptocurrency,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    if crud.crypto.exists(db, symbol=body.symbol):
        raise HTTPException(
            status_code=422,
            detail="Symbol already exists",
        )
    crud.crypto.create(db, body)
    return body.dict()


@router.get("/cryptocurrencies", status_code=200)
def get_cryptocurrencies(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)):
    return {
        "results": crud.crypto.get_all(db)
    }


@router.get("/cryptocurrencies/{cryptocurrency_id}", status_code=200)
def get_cryptocurrency(
        cryptocurrency_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    cryptocurrency = crud.crypto.get_by_id(db, cryptocurrency_id)
    if not cryptocurrency:
        raise HTTPException(
            status_code=404,
            detail="Cryptocurrency with given id does not exist",
        )
    return {
        "result": cryptocurrency
    }


@router.put("/cryptocurrencies/{cryptocurrency_id}", status_code=200)
def update_cryptocurrency(
        body: Cryptocurrency,
        cryptocurrency_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    old_cryptocurrency = crud.crypto.get_by_id(db, cryptocurrency_id)
    if not old_cryptocurrency:
        raise HTTPException(
            status_code=404,
            detail="Cryptocurrency with given id does not exist",
        )
    cryptocurrency = crud.crypto.update(db, old_cryptocurrency, body)
    return {
        "result": cryptocurrency
    }


@router.delete("/cryptocurrencies/{cryptocurrency_id}", status_code=204)
def delete_cryptocurrency(
        cryptocurrency_id: int,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    if not crud.crypto.get_by_id(db, cryptocurrency_id):
        raise HTTPException(
            status_code=404,
            detail="Cryptocurrency with given id does not exist",
        )
    crud.crypto.delete_by_id(db, cryptocurrency_id)


# Projects CRUD
@router.post("/projects/manage/{node_id}", status_code=200)
def manage_project(
        node_id: str,
        reserve_until: Optional[str] = None,
        is_paid: Optional[bool] = None,
        set_status: Optional[Literal["pending", "deploying", "active", "expired"]] = None,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    """
    Endpoint for managing the project status.

    reserve_until: ISO 8601
    """
    project = crud.projects.get_by_node_id_internal(db, node_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project with given id does not exist"
        )
    project, public_address = project
    if all(v is None for v in (reserve_until, is_paid, set_status)):
        raise HTTPException(
            status_code=422,
            detail="No changes specified"
        )
    if reserve_until:
        try:
            reserve_until = datetime.fromisoformat(reserve_until)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Incorrect date format"
            )
    project = crud.projects.manage_by_node_id_internal(db, project, reserve_until, is_paid, set_status)
    return {
        "result": ProjectResponse(
            node_id=project.node_id,
            cryptocurrency_symbol=project.cryptocurrency_symbol,
            cryptocurrency_full_name=crud.crypto.get_by_symbol(db, project.cryptocurrency_symbol).full_name,
            mode=project.mode.value,
            network=project.network.value,
            is_paid=project.is_paid,
            paid_until=str(project.paid_until),
            created_on=str(project.created_on),
            api_key=project.api_key,
            status=project.status,
            public_address=public_address,
            prefix=project.prefix
        )
    }


@router.get("/projects", status_code=200)
def list_projects(
        offset: int = None,
        limit: int = None,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    if offset and offset < 0 or limit and limit < 0:
        raise HTTPException(
            status_code=422,
            detail="Incorrect offset or limit format"
        )
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
                public_address=public_address,
                prefix=project.prefix
            ) for project, cryptocurrency_full_name, public_address in crud.projects.get_all_internal(db, limit=limit,
                                                                                                      offset=offset)
        ],
        "total": crud.projects.get_total_amount(db)
    }


@router.get("/projects/{public_address}", status_code=200)
def list_projects_for_address(
        public_address: str,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
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
                public_address=public_address,
                prefix=project.prefix
            ) for project, cryptocurrency_full_name, public_address in
            crud.projects.list_projects_by_public_address(db, public_address.lower())
        ]
    }


@router.delete("/projects/{node_id}", status_code=204)
def delete_project(
        node_id: str,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)
):
    project = crud.projects.get_by_node_id_internal(db, node_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project with given id does not exist"
        )
    project, _ = project
    crud.projects.delete_by_node_id_internal(db, node_id)


# Superadmin CRUD
@router.post("/superuser/{public_address}", status_code=204)
def add_superuser_rights(public_address: str,
                         db: Session = Depends(deps.get_db),
                         current_user: models.User = Depends(deps.get_current_active_superuser)):
    user: models.User = crud.user.get_user_by_address(db, public_address.lower())
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with given address does not exist"
        )
    if user.is_superuser:
        raise HTTPException(
            status_code=422,
            detail="User is already a superuser"
        )
    crud.user.update(db, db_obj=user, obj_in={
        "is_superuser": True
    })


@router.get("/superuser", status_code=200)
def list_superusers(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser)):

    return {
        "results": crud.user.get_superusers(db)
    }


@router.delete("/superuser/{public_address}", status_code=204)
def remove_superuser_rights(public_address: str,
                            db: Session = Depends(deps.get_db),
                            current_user: models.User = Depends(deps.get_current_active_superuser)):
    user: models.User = crud.user.get_user_by_address(db, public_address.lower())
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with given address does not exist"
        )
    if not user.is_superuser:
        raise HTTPException(
            status_code=422,
            detail="User is not a superuser"
        )
    if user.id == 1:
        raise HTTPException(
            status_code=422,
            detail="Master superuser can't be changed"
        )
    crud.user.update(db, db_obj=user, obj_in={
        "is_superuser": False
    })


@router.post("/projects/request/{public_address}", response_model=ProjectResponse)
def create_project(
        public_address: str,
        body: Project,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_superuser),
):
    user = crud.user.get_user_by_address(db, public_address.lower())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crypto = crud.crypto.get_by_symbol(db, body.cryptocurrency_symbol)
    if not crypto:
        raise HTTPException(
            status_code=404,
            detail="Cryptocurrency with given symbol does not exist"
        )
    new_project = ProjectDB(
        user_id=user.id,
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
        public_address=public_address.lower(),
        prefix=project.prefix
    )
