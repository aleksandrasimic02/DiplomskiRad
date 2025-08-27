from http.client import HTTPException

from fastapi import APIRouter, Depends, Query
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from app.db.session import get_db
from app.core.auth_deps import get_current_apoteka
from app.models.apoteka import Apoteka
from app.models.lek import Lek
from app.models.pretplata import Pretplata
from app.models.pretplata_lek import PretplataLek
from sqlalchemy import literal, case, func

router = APIRouter(prefix="/apoteka", tags=["Apotekarski portal"])

@router.get("/pregledajLekove")
def apoteka_pregledaj_lekove(
    apoteka: Apoteka = Depends(get_current_apoteka),
    db: Session = Depends(get_db),
    q: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    query = db.query(Lek).filter(Lek.id_apoteke == apoteka.id)
    if q:
        query = query.filter(Lek.naziv.ilike(f"%{q}%"))
    rows = query.order_by(Lek.naziv.asc()).limit(limit).offset(offset).all()
    return [
        {"id": r.id, "naziv": r.naziv, "cena": float(r.cena), "dostupnost": r.dostupnost, "potreban_recept": r.potreban_recept}
        for r in rows
    ]

@router.get("/pregledajPretplate")
def apoteka_pregledaj_pretplate(
    apoteka: Apoteka = Depends(get_current_apoteka),
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """
    Vraća pretplate koje sadrže makar jednu stavku iz OVE apoteke,
    zajedno sa statusom `aktivna`, datumom početka, ukupnom cenom itd.
    """
    # Pretplate koje imaju barem jednu stavku iz ove apoteke
    subq = (
        db.query(distinct(PretplataLek.id_pretplate))
        .join(Lek, PretplataLek.id_leka == Lek.id)
        .filter(Lek.id_apoteke == apoteka.id)
        .subquery()
    )

    rows = (
        db.query(
            Pretplata.id.label("pretplata_id"),
            Pretplata.naziv,
            Pretplata.datum_pocetka,
            Pretplata.dan_u_mesecu_dostave,
            Pretplata.aktivna.label("aktivna"),
            # broj stavki iz ove apoteke
            func.sum(case((Lek.id_apoteke == apoteka.id, 1), else_=0)).label("stavki_ove_apoteke"),
            # ukupno preko svih stavki (sve apoteke)
            func.sum(Lek.cena).label("ukupno"),
        )
        .join(PretplataLek, Pretplata.id == PretplataLek.id_pretplate)
        .join(Lek, Lek.id == PretplataLek.id_leka)
        .filter(Pretplata.id.in_(subq))
        .group_by(Pretplata.id)
        .order_by(Pretplata.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return [
        {
            "pretplata_id": r.pretplata_id,
            "naziv": r.naziv,
            "datum_pocetka": r.datum_pocetka.isoformat() if r.datum_pocetka else None,
            "dan_u_mesecu_dostave": r.dan_u_mesecu_dostave,
            "aktivna": bool(r.aktivna),                         # ⬅️ KLJUČNO
            "stavki_ove_apoteke": int(r.stavki_ove_apoteke or 0),
            "ukupno": float(r.ukupno or 0.0),
        }
        for r in rows
    ]

@router.get("/pretplate/{pretplata_id}/stavke")
def apoteka_pretplata_stavke(
    pretplata_id: int,
    db: Session = Depends(get_db),
    apoteka: Apoteka = Depends(get_current_apoteka),
):
    # 1) pretplata mora postojati
    p = db.query(Pretplata).filter(Pretplata.id == pretplata_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pretplata ne postoji.")

    # 2) bezbednosna provera: apoteka mora imati bar jednu stavku u ovoj pretplati
    ima_mojih = (
        db.query(PretplataLek.id)
        .join(Lek, Lek.id == PretplataLek.id_leka)
        .filter(PretplataLek.id_pretplate == pretplata_id, Lek.id_apoteke == apoteka.id)
        .first()
    )
    if not ima_mojih:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nema stavki iz ove apoteke u ovoj pretplati.")

    # 3) tolerantni atributi (ako su drugačije nazvani u modelu)
    recept_attr = getattr(PretplataLek, "recept_dokument", None) or getattr(PretplataLek, "recept", None) or literal(None)
    odobreno_attr = getattr(PretplataLek, "odobreno_apoteka", None) or getattr(PretplataLek, "odobreno", None) or literal(False)

    # 4) vrati SVE stavke te pretplate + flag "moja"

    rows = (
        db.query(
            PretplataLek.id.label("id"),
            PretplataLek.id_leka.label("id_leka"),
            recept_attr.label("recept_dokument"),
            odobreno_attr.label("odobreno_apoteka"),
            Lek.naziv.label("lek_naziv"),
            Lek.cena.label("cena"),
            Lek.id_apoteke.label("id_apoteke"),
            Lek.potreban_recept.label("potreban_recept"),  # ⬅️ NOVO
            case((Lek.id_apoteke == apoteka.id, True), else_=False).label("moja"),
        )
        .join(Lek, Lek.id == PretplataLek.id_leka)
        .filter(PretplataLek.id_pretplate == pretplata_id)
        .all()
    )

    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "id_leka": r.id_leka,
            "naziv": r.lek_naziv,
            "lek_naziv": r.lek_naziv,
            "cena": float(r.cena) if r.cena is not None else None,
            "recept_dokument": r.recept_dokument,
            "recept": r.recept_dokument,
            "odobreno_apoteka": bool(r.odobreno_apoteka),
            "id_apoteke": r.id_apoteke,
            "moja": bool(r.moja),
            "potreban_recept": bool(r.potreban_recept),  # ⬅️ NOVO
        })
    return out

@router.delete("/pretplate/{pretplata_id}", status_code=status.HTTP_204_NO_CONTENT)
def apoteka_obrisi_pretplatu(
    pretplata_id: int,
    apoteka: Apoteka = Depends(get_current_apoteka),
    db: Session = Depends(get_db),
):
    # 1) postoji?
    p = db.query(Pretplata).filter(Pretplata.id == pretplata_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pretplata ne postoji.")

    # 2) bezbednosno: apoteka mora imati bar jednu stavku u toj pretplati
    ima_mojih = (
        db.query(PretplataLek.id)
        .join(Lek, Lek.id == PretplataLek.id_leka)
        .filter(PretplataLek.id_pretplate == pretplata_id, Lek.id_apoteke == apoteka.id)
        .first()
    )
    if not ima_mojih:
        raise HTTPException(status_code=403, detail="Nemaš pravo da obrišeš ovu pretplatu.")

    # 3) obriši (ako nema DB cascade, ručno obriši stavke)
    db.query(PretplataLek).filter(PretplataLek.id_pretplate == pretplata_id).delete(synchronize_session=False)
    db.delete(p)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
