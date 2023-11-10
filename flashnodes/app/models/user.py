from sqlalchemy import VARCHAR, Boolean, Column, Integer, String

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    hashed_password = Column(VARCHAR(256), nullable=True)

    public_address = Column(VARCHAR(64), nullable=False, unique=True)
    nonce = Column(VARCHAR(64))  # Depends on nonce message length
