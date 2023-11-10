from typing import Optional

from pydantic import BaseModel, EmailStr, constr


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


# Metamask
class UserMetamaskCreate(BaseModel):
    public_address: constr()


class UserMetamaskCreateDB(UserMetamaskCreate):
    nonce: str


class UserMetamaskNonceResponse(UserMetamaskCreateDB):
    pass


class UserMetamaskVerify(UserMetamaskCreate):
    signed_nonce: str


class InitAdmin(UserMetamaskCreateDB, UserBase):
    email: EmailStr
    hashed_password: str


class EditUser(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
