from sqlalchemy.orm import Session
from app.models.staratelj import Staratelj
from app.schemas.staratelj import StarateljCreate

def create(db: Session, data: StarateljCreate) -> Staratelj:
    obj = Staratelj(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
