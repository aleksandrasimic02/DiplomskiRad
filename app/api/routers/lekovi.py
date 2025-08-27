from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.lek import LekCreate, LekOut
from app.crud import lek as crud

router = APIRouter(prefix="/lekovi", tags=["Lekovi"])

@router.post("", response_model=LekOut, status_code=201)
def create_lek(payload: LekCreate, db: Session = Depends(get_db)):
    try:
        obj = crud.create(db, payload)
        return obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
