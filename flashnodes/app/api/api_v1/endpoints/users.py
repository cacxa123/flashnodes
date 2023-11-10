from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.put("/me")
def update_user_me(
    body: schemas.EditUser,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    if not body.full_name and not body.email:
        raise HTTPException(
            status_code=422,
            detail="No data specified",
        )
    user = crud.user.update(db, db_obj=current_user, obj_in=body.dict(exclude_none=True))
    return {
        "public_address": user.public_address,
        "full_name": user.full_name,
        "email": user.email
    }


@router.get("/me")
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return {
        "public_address": current_user.public_address,
        "full_name": current_user.full_name,
        "email": current_user.email
    }
