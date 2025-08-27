# app/crud/pretplata.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.models.pretplata import Pretplata
from app.models.pretplata_lek import PretplataLek
from app.models.lek import Lek
from app.schemas.pretplata import PretplataCreate
from app.schemas.pretplata_lek import PretplataLekCreate

def _recompute_aktivna(db: Session, pretplata_id: int) -> Pretplata:
    """Aktivna je ako nema neodobrenih recept-stavki."""
    pending = (
        db.query(func.count())
        .select_from(PretplataLek)
        .join(Lek, Lek.id == PretplataLek.id_leka)
        .filter(
            PretplataLek.id_pretplate == pretplata_id,
            Lek.potreban_recept.is_(True),
            PretplataLek.odobreno_apoteka.is_(False),
        )
        .scalar()
    )
    p = db.get(Pretplata, pretplata_id)
    p.aktivna = (pending == 0)
    db.flush()
    return p

def create_pretplata(db: Session, data: PretplataCreate, owner_id: int) -> Pretplata:
    payload = data.model_dump() if hasattr(data, "model_dump") else data.dict()
    payload["id_korisnika"] = owner_id
    if not payload.get("datum_pocetka"):
        payload["datum_pocetka"] = date.today()
    # nova pretplata je aktivna dok se eventualno ne doda recept-stavka
    payload.setdefault("aktivna", True)

    obj = Pretplata(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def add_lek(db: Session, data: PretplataLekCreate, owner_id: int) -> PretplataLek:
    # 1) vlasništvo pretplate
    p = db.query(Pretplata).filter(
        Pretplata.id == data.id_pretplate,
        Pretplata.id_korisnika == owner_id
    ).first()
    if not p:
        raise ValueError("Pretplata ne postoji ili nije vaša.")

    # 2) lek
    lek = db.query(Lek).filter(Lek.id == data.id_leka).first()
    if not lek:
        raise ValueError("Lek ne postoji.")

    # 3) payload + alias
    payload = data.model_dump(by_alias=False) if hasattr(data, "model_dump") else data.dict()
    if "recept_dokument" not in payload and "recept" in payload:
        payload["recept_dokument"] = payload.pop("recept")

    # 4) pravila
    if getattr(lek, "potreban_recept", False):
        if not (payload.get("recept_dokument") and str(payload["recept_dokument"]).strip()):
            raise ValueError("Ovaj lek zahteva recept: pošaljite recept_dokument.")
        approved = False
    else:
        payload["recept_dokument"] = None
        approved = True

    if hasattr(PretplataLek, "odobreno_apoteka"):
        payload["odobreno_apoteka"] = approved

    # 5) insert + re-izračun aktivne pretplate
    obj = PretplataLek(**payload)
    db.add(obj)
    db.flush()                    # dobij obj.id, i imamo obj.id_pretplate
    _recompute_aktivna(db, p.id)  # ako je dodata recept-stavka → aktivna=False
    db.commit()
    db.refresh(obj)
    return obj
