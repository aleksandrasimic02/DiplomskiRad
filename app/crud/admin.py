from sqlalchemy.orm import Session
from app.models.admin import Administrator
from app.schemas.admin import AdminCreate

def create(db: Session, data: AdminCreate) -> Administrator:
    obj = Administrator(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
