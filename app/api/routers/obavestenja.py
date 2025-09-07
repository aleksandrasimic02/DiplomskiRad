# routers/obavestenja.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, join

# prilagodi import puteve svojim modulima
from app.db.session import get_db
from app.models import (
    Obavestenje,
    ObavestenjeKorisnik,
    ObavestenjeApoteka,
    ObavestenjeAdmin,
    Staratelj,
)
from app.core.auth_deps import (  # pretpostavka: ovde su tvoje auth dependency funkcije
    get_current_korisnik,
    get_current_apoteka,
    get_current_admin,
    get_current_staratelj,
)

router = APIRouter(prefix="/obavestenja", tags=["Obaveštenja"])


# ---------- Schemas ----------

class NotifOut(BaseModel):
    link_id: int
    naziv: str
    opis: str | None = None
    procitano: bool

class ToggleIn(BaseModel):
    link_id: int
    procitano: bool


# ---------- Helpers ----------

def _korisnik_list_query(db: Session, korisnik_id: int):
    """
    Vraća listu obaveštenja vezanih za korisnika.
    """
    stmt = (
        select(
            ObavestenjeKorisnik.id.label("link_id"),
            Obavestenje.naziv,
            Obavestenje.opis,
            ObavestenjeKorisnik.procitano,
        )
        .select_from(
            join(
                ObavestenjeKorisnik,
                Obavestenje,
                ObavestenjeKorisnik.obavestenje_id == Obavestenje.id,
            )
        )
        .where(ObavestenjeKorisnik.korisnik_id == korisnik_id)
        .order_by(ObavestenjeKorisnik.id.desc())
    )
    rows = db.execute(stmt).all()
    return [
        NotifOut(
            link_id=r.link_id, naziv=r.naziv, opis=r.opis, procitano=bool(r.procitano)
        )
        for r in rows
    ]


# ---------- LIST endpoints ----------

@router.get("/korisnik", response_model=list[NotifOut])
def list_for_korisnik(
    db: Session = Depends(get_db),
    korisnik=Depends(get_current_korisnik),
):
    """
    Ulogovani *korisnik* vidi svoja obaveštenja.
    """
    return _korisnik_list_query(db, korisnik.id)


@router.get("/korisnik/by-staratelj", response_model=list[NotifOut])
def list_korisnik_by_staratelj(
    korisnik_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    staratelj=Depends(get_current_staratelj),
):
    """
    Ulogovani *staratelj* vidi obaveštenja svog korisnika.
    Validiramo da staratelj zaista pripada tom korisniku i (po želji) da je odobren.
    """
    st = db.get(Staratelj, staratelj.id)
    if not st or st.id_korisnika != korisnik_id:
        raise HTTPException(status_code=403, detail="Nedozvoljen pristup obaveštenjima.")
    # opcionalno: zahtevaj odobren nalog
    # if not st.odobrio_admin: raise HTTPException(403, "Nalog staratelja nije odobren.")
    return _korisnik_list_query(db, korisnik_id)


@router.get("/apoteka", response_model=list[NotifOut])
def list_for_apoteka(
    db: Session = Depends(get_db),
    apoteka=Depends(get_current_apoteka),
):
    """
    Ulogovana *apoteka* vidi svoja obaveštenja.
    """
    stmt = (
        select(
            ObavestenjeApoteka.id.label("link_id"),
            Obavestenje.naziv,
            Obavestenje.opis,
            ObavestenjeApoteka.procitano,
        )
        .select_from(
            join(
                ObavestenjeApoteka,
                Obavestenje,
                ObavestenjeApoteka.obavestenje_id == Obavestenje.id,
            )
        )
        .where(ObavestenjeApoteka.apoteka_id == apoteka.id)
        .order_by(ObavestenjeApoteka.id.desc())
    )
    rows = db.execute(stmt).all()
    return [
        NotifOut(
            link_id=r.link_id, naziv=r.naziv, opis=r.opis, procitano=bool(r.procitano)
        )
        for r in rows
    ]


@router.get("/admin", response_model=list[NotifOut])
def list_for_admin(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Ulogovani *admin* vidi svoja obaveštenja.
    """
    stmt = (
        select(
            ObavestenjeAdmin.id.label("link_id"),
            Obavestenje.naziv,
            Obavestenje.opis,
            ObavestenjeAdmin.procitano,
        )
        .select_from(
            join(
                ObavestenjeAdmin,
                Obavestenje,
                ObavestenjeAdmin.obavestenje_id == Obavestenje.id,
            )
        )
        .where(ObavestenjeAdmin.admin_id == admin.id)
        .order_by(ObavestenjeAdmin.id.desc())
    )
    rows = db.execute(stmt).all()
    return [
        NotifOut(
            link_id=r.link_id, naziv=r.naziv, opis=r.opis, procitano=bool(r.procitano)
        )
        for r in rows
    ]


# ---------- TOGGLE endpoints ----------

@router.post("/korisnik/toggle")
def toggle_korisnik(
    payload: ToggleIn,
    db: Session = Depends(get_db),
    korisnik=Depends(get_current_korisnik),
):
    link = db.get(ObavestenjeKorisnik, payload.link_id)
    if not link or link.korisnik_id != korisnik.id:
        raise HTTPException(status_code=404, detail="Veza obaveštenja nije pronađena.")
    link.procitano = bool(payload.procitano)
    db.commit()
    return {"ok": True, "link_id": link.id, "procitano": link.procitano}


@router.post("/korisnik/toggle/by-staratelj")
def toggle_korisnik_by_staratelj(
    payload: ToggleIn,
    korisnik_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    staratelj=Depends(get_current_staratelj),
):
    st = db.get(Staratelj, staratelj.id)
    if not st or st.id_korisnika != korisnik_id:
        raise HTTPException(status_code=403, detail="Zabranjeno menjanje ovog obaveštenja.")
    link = db.get(ObavestenjeKorisnik, payload.link_id)
    if not link or link.korisnik_id != korisnik_id:
        raise HTTPException(status_code=404, detail="Veza obaveštenja nije pronađena.")
    link.procitano = bool(payload.procitano)
    db.commit()
    return {"ok": True, "link_id": link.id, "procitano": link.procitano}


@router.post("/apoteka/toggle")
def toggle_apoteka(
    payload: ToggleIn,
    db: Session = Depends(get_db),
    apoteka=Depends(get_current_apoteka),
):
    link = db.get(ObavestenjeApoteka, payload.link_id)
    if not link or link.apoteka_id != apoteka.id:
        raise HTTPException(status_code=404, detail="Veza obaveštenja nije pronađena.")
    link.procitano = bool(payload.procitano)
    db.commit()
    return {"ok": True, "link_id": link.id, "procitano": link.procitano}


@router.post("/admin/toggle")
def toggle_admin(
    payload: ToggleIn,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    link = db.get(ObavestenjeAdmin, payload.link_id)
    if not link or link.admin_id != admin.id:
        raise HTTPException(status_code=404, detail="Veza obaveštenja nije pronađena.")
    link.procitano = bool(payload.procitano)
    db.commit()
    return {"ok": True, "link_id": link.id, "procitano": link.procitano}
