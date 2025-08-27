from sqlalchemy.orm import Session
from app.models.apoteka import Apoteka
from app.schemas.apoteka import ApotekaCreate

def create(db: Session, data: ApotekaCreate) -> Apoteka:
    obj = Apoteka(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
