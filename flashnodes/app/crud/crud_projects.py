from datetime import datetime
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import User
from app.models.projects import Projects
from app.models.cryptocurrencies import Cryptocurrencies
from app.schemas import Project, ProjectDB


class CRUDProjects(CRUDBase[Projects, Project, Project]):
    def create(self, db: Session, obj_in: ProjectDB):
        db_obj = Projects(
            user_id=obj_in.user_id,
            cryptocurrency_symbol=obj_in.cryptocurrency_symbol,
            mode=obj_in.mode,
            network=obj_in.network,
            paid_until=obj_in.pay_until,
            prefix=obj_in.prefix
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_all(self, db: Session, user_id: int, limit: int = None, offset: int = None):
        return db.query(Projects, Cryptocurrencies.full_name).join(
            Cryptocurrencies, Cryptocurrencies.symbol == Projects.cryptocurrency_symbol
        ).filter(Projects.user_id == user_id).limit(limit).offset(offset).all()

    def get_all_internal(self, db: Session, limit: int = None, offset: int = None):
        return db.query(Projects, Cryptocurrencies.full_name, User.public_address).join(
            Cryptocurrencies, Cryptocurrencies.symbol == Projects.cryptocurrency_symbol
        ).join(
            User, User.id == Projects.user_id
        ).filter().order_by(desc(Projects.id)).limit(limit).offset(offset).all()

    def get_total_amount(self, db: Session):
        return db.query(Projects).count()

    def get_by_id(self, db: Session, project_id: int, user_id: int):
        return db.query(Projects).filter(Projects.id == project_id,
                                         Projects.user_id == user_id).first()

    def get_by_node_id(self, db: Session, node_id: int, user_id: int):
        return db.query(Projects, Cryptocurrencies.full_name).join(
            Cryptocurrencies, Cryptocurrencies.symbol == Projects.cryptocurrency_symbol
        ).filter(Projects.node_id == node_id, Projects.user_id == user_id).first()

    def get_by_node_id_internal(self, db: Session, node_id: str):
        return db.query(Projects, User.public_address).filter(Projects.node_id == node_id).join(
            User, User.id == Projects.user_id
        ).first()

    def delete_by_node_id_internal(self, db: Session, node_id: int):
        db.query(Projects).filter(Projects.node_id == node_id).delete()
        db.commit()

    def manage_by_node_id_internal(self, db: Session, db_obj: Projects, paid_until: Optional[datetime] = None,
                                   is_paid: bool = None, set_status: str = None):
        obj_in = {}
        if is_paid:
            obj_in["is_paid"] = is_paid
        if paid_until:
            obj_in["paid_until"] = paid_until
        if set_status:
            obj_in["status"] = set_status
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def list_projects_by_public_address(self, db: Session, public_address: str):
        return db.query(Projects, Cryptocurrencies.full_name, User.public_address).join(
            Cryptocurrencies, Cryptocurrencies.symbol == Projects.cryptocurrency_symbol
        ).join(
            User, User.public_address == public_address
        ).all()

    def get_api_key_by_node_id(self, db: Session, user_id: int, node_id: str):
        return db.query(Projects.api_key).filter(User.id == user_id,
                                                 Projects.node_id == node_id).first()

    def get_all_api_keys(self, db: Session, user_id: int):
        return db.query(Projects.api_key).join(User, User.id == user_id).all()


projects = CRUDProjects(Projects)
