from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.core.security import get_password_hash
from app.db import base  # noqa: F401
from app.utils import generate_nonce_url_safe

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    user = crud.user.get_by_email(db, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = schemas.InitAdmin(
            email=settings.FIRST_SUPERUSER,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            is_superuser=True,
            public_address=settings.FIRST_PUBLIC_ADDRESS.lower(),
            nonce=generate_nonce_url_safe()
        )
        user = crud.user.create(db, obj_in=user_in)  # noqa: F841
