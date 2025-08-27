# app/api/routers/pretplate.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import literal
from app.db.session import get_db
from app.schemas.pretplata import PretplataCreate, PretplataOut
from app.schemas.pretplata_lek import PretplataLekCreate, PretplataLekOut
from app.crud.pretplata import create_pretplata, add_lek
from app.core.auth_deps import get_pretplate_owner_id   # ⬅️ novo
from app.models.pretplata import Pretplata              # (za zaštitu kod otkazivanja, ako je u ovom fajlu)
from app.models.pretplata_lek import PretplataLek
from app.models.lek import Lek

router = APIRouter(prefix="/pretplate", tags=["Pretplate"])

@router.post("", response_model=PretplataOut, status_code=201)
def create(
    payload: PretplataCreate,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_pretplate_owner_id),  # ⬅️ ključna linija
):
    try:
        return create_pretplata(db, payload, owner_id=owner_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stavke", response_model=PretplataLekOut, status_code=201)
def add_item(
    payload: PretplataLekCreate,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_pretplate_owner_id),  # ⬅️ isto
):
    try:
        return add_lek(db, payload, owner_id=owner_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def _list_stavke_for(db: Session, owner_id: int, pretplata_id: int):
    # 1) provera vlasništva
    p = db.query(Pretplata).filter(
        Pretplata.id == pretplata_id,
        Pretplata.id_korisnika == owner_id,
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pretplata ne postoji ili nije vaša.")

    # 2) tolerantno uzmi kolone (mogu da ne postoje)
    recept_attr = getattr(PretplataLek, "recept_dokument", None) or getattr(PretplataLek, "recept", None) or literal(None)
    odobreno_attr = getattr(PretplataLek, "odobreno_apoteka", None) or getattr(PretplataLek, "odobreno", None) or literal(False)

    cols = [
        PretplataLek.id.label("id"),
        PretplataLek.id_leka.label("id_leka"),
        recept_attr.label("recept_dokument"),
        odobreno_attr.label("odobreno_apoteka"),
        Lek.naziv.label("lek_naziv"),
        Lek.cena.label("cena"),
        Lek.potreban_recept.label("potreban_recept"),  # ⬅️ NOVO
    ]
    rows = (
        db.query(*cols)
        .join(Lek, Lek.id == PretplataLek.id_leka)
        .filter(PretplataLek.id_pretplate == pretplata_id)  # ili PretplataLek.pretplata_id
        .all()
    )

    out = []
    for r in rows:
        # r je Row sa ključevima iz label-a
        cena_val = float(r.cena) if r.cena is not None else None
        val = {
            "id": r.id,
            "id_leka": r.id_leka,
            "naziv": r.lek_naziv,
            "lek_naziv": r.lek_naziv,
            "cena": cena_val,
            "recept_dokument": r.recept_dokument,
            "recept": r.recept_dokument,  # alias da frontend radi i sa s.recept
            "odobreno_apoteka": bool(r.odobreno_apoteka),
            "potreban_recept": bool(r.potreban_recept),
        }
        out.append(val)
    return out

@router.get("/stavke")
def list_stavke_qp(
    pretplata_id: int,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_pretplate_owner_id),
):
    return _list_stavke_for(db, owner_id, pretplata_id)

@router.get("/{pretplata_id}/stavke")
def list_stavke_pp(
    pretplata_id: int,
    db: Session = Depends(get_db),
    owner_id: int = Depends(get_pretplate_owner_id),
):
    return _list_stavke_for(db, owner_id, pretplata_id)