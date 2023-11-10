from datetime import datetime, timedelta
from typing import Literal, Optional

from pydantic import UUID4, BaseModel, validator


class ProjectBase(BaseModel):
    cryptocurrency_symbol: str
    mode: Literal["full", "archived"]
    network: Literal["mainnet", "testnet"]


class Project(ProjectBase):
    @validator("pay_until", pre=True)
    def parse_iso_date(cls, value):
        date = datetime.fromisoformat(value)
        assert date <= date + timedelta(days=1)
        return value
    pay_until: str


class ProjectDB(Project):
    user_id: int
    prefix: str


class ProjectResponse(ProjectBase):
    node_id: UUID4
    is_paid: bool
    paid_until: Optional[str]
    created_on: str
    api_key: UUID4
    status: Optional[str]
    cryptocurrency_full_name: str
    public_address: Optional[str]
    prefix: str
