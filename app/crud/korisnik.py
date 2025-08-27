from sqlalchemy.orm import Session
from app.models.korisnik import Korisnik
from app.schemas.korisnik import KorisnikCreate

def create(db: Session, data: KorisnikCreate) -> Korisnik:
    obj = Korisnik(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
