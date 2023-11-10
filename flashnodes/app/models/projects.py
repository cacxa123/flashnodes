from sqlalchemy import (
    BOOLEAN,
    TIMESTAMP,
    VARCHAR,
    Column,
    ForeignKey,
    Integer,
    false,
    text,
)
from sqlalchemy_utils import ChoiceType
from sqlalchemy_utils.types import UUIDType

from app.db.base_class import Base


class Projects(Base):
    MODES = [
        ("full", "full"),
        ("archived", "archived")
    ]
    NETWORKS = [
        ("mainnet", "mainnet"),
        ("testnet", "testnet")
    ]

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(UUIDType(binary=False), index=True, nullable=False, server_default=text("gen_random_uuid()"))
    user_id = Column(Integer, ForeignKey("user.id"))
    cryptocurrency_symbol = Column(VARCHAR(12), ForeignKey("cryptocurrencies.symbol"))

    status = Column(VARCHAR(9), nullable=False, server_default="pending")
    mode = Column(ChoiceType(MODES, impl=VARCHAR(8)), nullable=False)
    network = Column(ChoiceType(NETWORKS, impl=VARCHAR(7)), nullable=False)
    is_paid = Column(BOOLEAN, nullable=False, server_default=false())
    paid_until = Column(TIMESTAMP, nullable=True)
    created_on = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    api_key = Column(UUIDType(binary=False), nullable=False, server_default=text("gen_random_uuid()"))
    prefix = Column(VARCHAR(8), nullable=False)
