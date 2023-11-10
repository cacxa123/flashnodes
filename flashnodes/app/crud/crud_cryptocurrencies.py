from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.cryptocurrencies import Cryptocurrencies
from app.schemas.cryptocurrency import Cryptocurrency


class CRUDCryptocurrencies(CRUDBase[Cryptocurrencies, Cryptocurrency, Cryptocurrency]):
    def create(self, db: Session, obj_in: Cryptocurrency):
        db_obj = Cryptocurrencies(
            full_name=obj_in.full_name,
            symbol=obj_in.symbol,
            details=obj_in.details
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def exists(self, db: Session, symbol: str):
        return db.query(Cryptocurrencies).filter(Cryptocurrencies.symbol == symbol).first() is not None

    def get_all(self, db: Session):
        return db.query(Cryptocurrencies).all()

    def get_by_id(self, db: Session, cryptocurrency_id: int):
        return db.query(Cryptocurrencies).filter(Cryptocurrencies.id == cryptocurrency_id).first()

    def get_by_symbol(self, db: Session, symbol: str):
        return db.query(Cryptocurrencies).filter(Cryptocurrencies.symbol == symbol).first()

    def delete_by_id(self, db: Session, cryptocurrency_id: int):
        db.query(Cryptocurrencies).filter(Cryptocurrencies.id == cryptocurrency_id).delete()
        db.commit()

    def update(
        self, db: Session, db_obj: Cryptocurrencies, obj_in: Cryptocurrency
    ) -> Cryptocurrencies:
        update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)


crypto = CRUDCryptocurrencies(Cryptocurrencies)
