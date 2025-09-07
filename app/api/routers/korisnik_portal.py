from app.crud.obavestenje import add_apoteka, add_korisnik
from app.models.lek import Lek
from fastapi import APIRouter, Depends, HTTPException, status, Response

from app.core.auth_deps import get_korisnik_id_from_korisnik_or_staratelj, get_current_korisnik
from app.models.pretplata import Pretplata
from app.models.pretplata_lek import PretplataLek

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.db.session import get_db
from app.core.auth_deps import get_current_korisnik
from app.models.staratelj import Staratelj

router = APIRouter(prefix="/korisnik", tags=["Korisnički portal"])

class StarateljOut(BaseModel):
    id: int
    ime: str
    prezime: Optional[str] = None
    email: Optional[str] = None
    broj_telefona: Optional[str] = None
    dokument_starateljstva: Optional[str] = None
    odobrio_admin: Optional[bool] = None
    id_korisnika: int

    class Config:
        from_attributes = True  # (SQLAlchemy -> Pydantic)

@router.get("/pregledajPretplate")
def pregledaj_pretplate(korisnik_id: int = Depends(get_korisnik_id_from_korisnik_or_staratelj),
                        db: Session = Depends(get_db)):
    rows: ListP = db.query(Pretplata).filter(Pretplata.id_korisnika == korisnik_id).order_by(Pretplata.id.desc()).all()
    out = []
    for p in rows:
        count_items = db.query(PretplataLek).filter(PretplataLek.id_pretplate == p.id).count()
        out.append({
            "pretplata_id": p.id,
            "naziv": p.naziv,
            "dan_u_mesecu_dostave": p.dan_u_mesecu_dostave,
            "aktivna": p.aktivna,
            "broj_stavki": count_items
        })
    return out

# --- kreiranje / otkazivanje pretplate (samo vlasnik korisnik, ne staratelj) ---

from pydantic import BaseModel, conint
from datetime import date

class PretplataCreateIn(BaseModel):
    naziv: str
    dan_u_mesecu_dostave: conint(ge=1, le=28)
    datum_pocetka: date | None = None

@router.post("/dodajPretplatu", status_code=201)
def dodaj_pretplatu(payload: PretplataCreateIn,
                    korisnik = Depends(get_current_korisnik),
                    db: Session = Depends(get_db)):
    p = Pretplata(
        id_korisnika=korisnik.id,
        naziv=payload.naziv,
        dan_u_mesecu_dostave=payload.dan_u_mesecu_dostave,
        datum_pocetka=payload.datum_pocetka or date.today(),
        aktivna=True
    )
    db.add(p); db.commit(); db.refresh(p)
    return {"pretplata_id": p.id}

class PretplataIdIn(BaseModel):
    pretplata_id: int

@router.delete("/pretplate/{pretplata_id}", status_code=status.HTTP_204_NO_CONTENT)
def korisnik_obrisi_pretplatu(
    pretplata_id: int,
    korisnik = Depends(get_current_korisnik),
    db: Session = Depends(get_db),
):
    p = db.query(Pretplata).filter(
        Pretplata.id == pretplata_id,
        Pretplata.id_korisnika == korisnik.id
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pretplata nije pronađena.")

    apoteka_ids = [
        aid for (aid,) in (
            db.query(Lek.id_apoteke)
              .join(PretplataLek, PretplataLek.id_leka == Lek.id)
              .filter(PretplataLek.id_pretplate == pretplata_id)
              .distinct()
              .all()
        ) if aid is not None
    ]
    db.query(PretplataLek).filter(PretplataLek.id_pretplate == pretplata_id).delete(synchronize_session=False)
    db.delete(p)
    db.commit()
    add_korisnik(db=db, obavestenje_id=7, korisnik_id=korisnik.id)
    for aid in apoteka_ids:
            add_apoteka(db=db, obavestenje_id=7, apoteka_id=aid)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/obrisiNalog", status_code=204)
def obrisi_nalog(korisnik = Depends(get_current_korisnik),
                 db: Session = Depends(get_db)):
    # kaskadno će obrisati pretplate i staratelje (po FK pravilima)
    db.delete(korisnik)
    db.commit()
    return


@router.get("/staratelji", response_model=List[StarateljOut])
def korisnik_staratelji(
    korisnik = Depends(get_current_korisnik),
    db: Session = Depends(get_db),
):
    """
    Vrati sve staratelje vezane za ulogovanog korisnika.
    Ako nema staratelja, vraća se prazna lista.
    """
    rows = (
        db.query(Staratelj)
        .filter(Staratelj.id_korisnika == korisnik.id)
        .order_by(Staratelj.id.asc())
        .all()
    )
    return rows