from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic.networks import EmailStr

from app import models, schemas
from app.api import deps
from app.core.celery_app import celery_app
from app.utils import send_test_email

router = APIRouter()


@router.post("/test-celery/", response_model=schemas.Msg, status_code=201)
def test_celery(
    msg: schemas.Msg,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test Celery worker.
    """
    celery_app.send_task("app.worker.test_celery", args=[msg.msg])
    return {"msg": "Word received"}


@router.post("/test-email/", response_model=schemas.Msg, status_code=201, deprecated=True)
def test_email(
    email_to: EmailStr,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}


@router.post("/test-datetime/{datetime_iso}", status_code=200)
def test_datetime_format(datetime_iso: str,
                         current_user: models.User = Depends(deps.get_current_active_superuser)):
    """
    Test datetime format for project request approval (ISO 8601)
    """
    try:
        datetime_parsed = datetime.fromisoformat(datetime_iso)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Incorrect date format"
        )
    return {
        "datetime_parsed": datetime_parsed,
        "unix_timestamp": int(datetime_parsed.timestamp())
    }
