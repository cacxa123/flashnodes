from sqlalchemy import TEXT, VARCHAR, Column, Integer

from app.db.base_class import Base


class Cryptocurrencies(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(VARCHAR(64), nullable=False)
    symbol = Column(VARCHAR(12), nullable=False, unique=True)
    details = Column(TEXT, nullable=True)
