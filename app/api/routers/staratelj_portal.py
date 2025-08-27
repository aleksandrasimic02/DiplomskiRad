from fastapi import APIRouter, Depends, Response, status, HTTPException

from app.models.pretplata import Pretplata
from app.models.pretplata_lek import PretplataLek
from datetime import date


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.db.session import get_db
from app.core.auth_deps import get_current_staratelj
from app.models.korisnik import Korisnik
from app.models.staratelj import Staratelj

router = APIRouter(prefix="/staratelj", tags=["Staratelj portal"])

@router.delete("/obrisiNalog", status_code=204)
def obrisi_nalog(staratelj: Staratelj = Depends(get_current_staratelj), db: Session = Depends(get_db)):
    db.delete(staratelj)
    db.commit()
    return

@router.delete("/pretplate/{pretplata_id}", status_code=status.HTTP_204_NO_CONTENT)
def staratelj_obrisi_pretplatu(
    pretplata_id: int,
    staratelj: Staratelj = Depends(get_current_staratelj),
    db: Session = Depends(get_db),
):
    # dozvoljeno je brisanje samo pretplate korisnika nad kojim je staratelj postavljen
    p = db.query(Pretplata).filter(
        Pretplata.id == pretplata_id,
        Pretplata.id_korisnika == staratelj.id_korisnika,
    ).first()

    if not p:
        raise HTTPException(status_code=404, detail="Pretplata nije pronađena za korisnika kog nadzirete.")

    # obriši stavke pa pretplatu
    db.query(PretplataLek).filter(PretplataLek.id_pretplate == pretplata_id).delete(synchronize_session=False)
    db.delete(p)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


class KorisnikOut(BaseModel):
    id: int
    ime: str
    prezime: Optional[str] = None
    email: Optional[str] = None
    broj_telefona: Optional[str] = None
    datum_rodjenja: date | None = None   # ⬅️ promenjeno
    adresa: Optional[str] = None

    class Config:
        from_attributes = True  # SQLAlchemy -> Pydantic (v2)

# ── Endpoint ───────────────────────────────────────────────────────────────────
@router.get("/korisnik", response_model=KorisnikOut)
def staratelj_korisnik(
    staratelj: Staratelj = Depends(get_current_staratelj),
    db: Session = Depends(get_db),
):
    """
    Vrati korisnika kome je ulogovani staratelj pridružen.
    """
    k = db.query(Korisnik).filter(Korisnik.id == staratelj.id_korisnika).first()
    if not k:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen.")
    return k