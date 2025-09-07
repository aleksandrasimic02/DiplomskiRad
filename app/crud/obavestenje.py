from typing import Iterable, Sequence
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.models.obavestenje import (
    ObavestenjeAdmin,
    ObavestenjeKorisnik,
    ObavestenjeApoteka,
)

# ------------ ADMIN ------------
def add_admin(db: Session, *, obavestenje_id: int, admin_id: int, procitano: bool = False) -> None:
    stmt = insert(ObavestenjeAdmin).values(
        obavestenje_id=obavestenje_id, admin_id=admin_id, procitano=procitano
    ).on_conflict_do_nothing(constraint="uq_obav_admin")
    db.execute(stmt)
    db.commit()




# ------------ KORISNIK ------------
def add_korisnik(db: Session, *, obavestenje_id: int, korisnik_id: int, procitano: bool = False) -> None:
    stmt = insert(ObavestenjeKorisnik).values(
        obavestenje_id=obavestenje_id, korisnik_id=korisnik_id, procitano=procitano
    ).on_conflict_do_nothing(constraint="uq_obav_korisnik")
    db.execute(stmt)
    db.commit()



# ------------ APOTEKA ------------
def add_apoteka(db: Session, *, obavestenje_id: int, apoteka_id: int, procitano: bool = False) -> None:
    stmt = insert(ObavestenjeApoteka).values(
        obavestenje_id=obavestenje_id, apoteka_id=apoteka_id, procitano=procitano
    ).on_conflict_do_nothing(constraint="uq_obav_apoteka")
    db.execute(stmt)
    db.commit()

