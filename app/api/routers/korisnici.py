from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.korisnik import KorisnikCreate, KorisnikOut
from app.crud import korisnik as crud

router = APIRouter(prefix="/korisnici", tags=["Korisnici"])

@router.post("", response_model=KorisnikOut, status_code=201)
def create_korisnik(payload: KorisnikCreate, db: Session = Depends(get_db)):
    try:
        obj = crud.create(db, payload)
        return obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
