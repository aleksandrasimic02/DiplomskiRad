from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.apoteka import ApotekaCreate, ApotekaOut
from app.crud import apoteka as crud

router = APIRouter(prefix="/apoteke", tags=["Apoteke"])

@router.post("", response_model=ApotekaOut, status_code=201)
def create_apoteka(payload: ApotekaCreate, db: Session = Depends(get_db)):
    try:
        obj = crud.create(db, payload)
        return obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
