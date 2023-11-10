from datetime import timedelta
from typing import Any

from eth_account import Account, messages
from eth_utils import is_address
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.utils import (
    generate_nonce_url_safe,
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.get("/metamask/nonce/{public_address}", response_model=schemas.UserMetamaskNonceResponse)
def get_associated_nonce(
    public_address: str,
    db: Session = Depends(deps.get_db)
):
    public_address = public_address.lower()
    if not is_address(public_address):
        raise HTTPException(status_code=422, detail="Incorrect address")

    nonce = generate_nonce_url_safe()
    nonce_result = schemas.UserMetamaskCreateDB(public_address=public_address,
                                                nonce=nonce)
    user = crud.user.get_user_by_address(db, public_address)
    if not user:
        crud.user.create_metamask(db, nonce_result)
    else:
        crud.user.update_nonce(db, user, nonce)
    return nonce_result


@router.post("/auth", response_model=schemas.Token)
def login_via_metamask(
    body: schemas.UserMetamaskVerify,
    db: Session = Depends(deps.get_db)
):
    public_address = body.public_address.lower()
    if not is_address(public_address):
        raise HTTPException(status_code=422, detail="Incorrect address")

    user = crud.user.get_user_by_address(db, public_address)
    if not user:
        raise HTTPException(status_code=403, detail="Associated nonce does not exist")
    nonce = messages.encode_defunct(text=user.nonce)

    if not Account.recover_message(nonce, signature=body.signed_nonce).lower() == public_address:
        raise HTTPException(status_code=403, detail="Nonce signature couldn't been verified")

    new_nonce = generate_nonce_url_safe()
    crud.user.update_nonce(db, user, new_nonce)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "nonce": new_nonce
    }


@router.post("/test-token", response_model=schemas.User)
def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}", response_model=schemas.Msg, deprecated=True)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = crud.user.get_by_email(db, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", response_model=schemas.Msg, deprecated=True)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}
