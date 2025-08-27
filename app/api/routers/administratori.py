from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.admin import AdminCreate, AdminOut
from app.crud import admin as crud

router = APIRouter(prefix="/administratori", tags=["Administratori"])

@router.post("", response_model=AdminOut, status_code=201)
def create_admin(payload: AdminCreate, db: Session = Depends(get_db)):
    try:
        obj = crud.create(db, payload)
        return obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
