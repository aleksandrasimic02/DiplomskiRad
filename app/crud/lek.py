from sqlalchemy.orm import Session
from app.models.lek import Lek
from app.schemas.lek import LekCreate

def create(db: Session, data: LekCreate) -> Lek:
    obj = Lek(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
