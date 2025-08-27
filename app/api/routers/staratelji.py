from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.staratelj import StarateljCreate, StarateljOut
from app.crud import staratelj as crud

router = APIRouter(prefix="/staratelji", tags=["Staratelji"])

@router.post("", response_model=StarateljOut, status_code=201)
def create_staratelj(payload: StarateljCreate, db: Session = Depends(get_db)):
    try:
        obj = crud.create(db, payload)
        return obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
