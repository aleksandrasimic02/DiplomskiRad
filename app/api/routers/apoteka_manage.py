from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field
from typing import Optional
from app.db.session import get_db
from app.core.auth_deps import get_current_apoteka
from app.models.apoteka import Apoteka
from app.models.lek import Lek
from app.models.pretplata import Pretplata
from app.models.pretplata_lek import PretplataLek
from sqlalchemy import func, or_
from app.crud.pretplata import _recompute_aktivna

router = APIRouter(prefix="/apoteka", tags=["Apotekarski menadžment"])

# --- dodaj / obriši lek ---
class PretplataApproveIn(BaseModel):
    pretplata_id: int

class PretplataStatusOut(BaseModel):
    pretplata_id: int
    aktivna: bool
    message: str | None = None
class LekIn(BaseModel):
    naziv: str
    cena: float = Field(ge=0)
    potreban_recept: bool = False
    dostupnost: bool = True

@router.post("/dodajLek", status_code=201)
def dodaj_lek(payload: LekIn, apoteka: Apoteka = Depends(get_current_apoteka), db: Session = Depends(get_db)):
    # Jedinstveno u okviru apoteke
    if db.query(Lek.id).filter(Lek.id_apoteke == apoteka.id, Lek.naziv == payload.naziv).first():
        raise HTTPException(status_code=400, detail="Lek sa tim nazivom već postoji u ovoj apoteci.")
    l = Lek(
        id_apoteke=apoteka.id,
        naziv=payload.naziv,
        cena=payload.cena,
        potreban_recept=payload.potreban_recept,
        dostupnost=payload.dostupnost
    )
    db.add(l); db.commit(); db.refresh(l)
    return {"lek_id": l.id}

class LekIdIn(BaseModel):
    lek_id: int

@router.delete("/obrisiLek", status_code=204)
def obrisi_lek(payload: LekIdIn, apoteka: Apoteka = Depends(get_current_apoteka), db: Session = Depends(get_db)):
    l = db.query(Lek).filter(Lek.id == payload.lek_id, Lek.id_apoteke == apoteka.id).first()
    if not l:
        raise HTTPException(status_code=404, detail="Lek nije pronađen u ovoj apoteci.")
    db.delete(l); db.commit()
    return

# --- odobri pretplatu (stavke iz ove apoteke koje traže recept i imaju dokument) ---

class PretplataApproveIn(BaseModel):
    pretplata_id: int

@router.post("/odobriPretplatu", response_model=PretplataStatusOut)
def odobri_pretplatu(
    payload: PretplataApproveIn,
    apoteka = Depends(get_current_apoteka),
    db: Session = Depends(get_db),
):
    # 1) Proveri da pretplata postoji
    p = db.get(Pretplata, payload.pretplata_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pretplata ne postoji.")

    # 2) Sve RECEPTNE stavke iz OVE apoteke za datu pretplatu koje još nisu odobrene
    items = (
        db.query(PretplataLek)
          .join(Lek, Lek.id == PretplataLek.id_leka)
          .filter(
              PretplataLek.id_pretplate == p.id,
              Lek.id_apoteke == apoteka.id,
              Lek.potreban_recept.is_(True),
              # ako želiš da setuješ i već odobrene ponovo na True, skini ovaj filter
              (PretplataLek.odobreno_apoteka.is_(False) | PretplataLek.odobreno_apoteka.is_(None))
          )
          .all()
    )

    # 3) Označi kao odobrene (pretpostavljamo da recept_dokument postoji – to je već
    #    validirano pri insertu kroz trigger/CRUD)
    for it in items:
        it.odobreno_apoteka = True

    # 4) Re-izračunaj status pretplate na osnovu svih stavki (sve apoteke)
    db.flush()
    _recompute_aktivna(db, p.id)
    db.commit()
    db.refresh(p)
    print(p.aktivna)

    if not items:
        return PretplataStatusOut(
            pretplata_id=p.id,
            aktivna=p.aktivna,
            message="Nema stavki za odobravanje u ovoj apoteci."
        )

    return PretplataStatusOut(
        pretplata_id=p.id,
        aktivna=p.aktivna,
        message=f"Odobreno stavki iz ove apoteke: {len(items)}."
    )

