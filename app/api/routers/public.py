from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.models.lek import Lek
from app.models.apoteka import Apoteka

router = APIRouter(tags=["Javno"])

@router.get("/pregledajLekove")
def pregledaj_lekove(db: Session = Depends(get_db), q: str | None = None, samo_dostupni: bool = True):
    qy = (
        db.query(
            Lek.id, Lek.naziv, Lek.cena, Lek.dostupnost, Lek.potreban_recept,
            Apoteka.id.label("id_apoteke"),
            Apoteka.naziv.label("apoteka_naziv"),
            Apoteka.adresa.label("apoteka_adresa"),
        )
        .join(Apoteka, Apoteka.id == Lek.id_apoteke)
    )
    if q:
        qy = qy.filter(Lek.naziv.ilike(f"%{q}%"))
    if samo_dostupni:
        qy = qy.filter(Lek.dostupnost.is_(True))
    rows = qy.order_by(Apoteka.naziv.asc(), Lek.naziv.asc()).all()
    return [
        dict(
            id=r.id,
            naziv=r.naziv,
            cena=float(r.cena),
            dostupnost=bool(r.dostupnost),
            potreban_recept=bool(r.potreban_recept),
            id_apoteke=r.id_apoteke,
            apoteka_naziv=r.apoteka_naziv,
            apoteka_adresa=r.apoteka_adresa,
        )
        for r in rows
    ]

@router.get("/pregledajApoteke")
def pregledaj_apoteke(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, description="Pretraga po nazivu, mejlu ili adresi"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    query = db.query(Apoteka)
    if q:
        query = query.filter(
            or_(Apoteka.naziv.ilike(f"%{q}%"), Apoteka.mejl.ilike(f"%{q}%"), Apoteka.adresa.ilike(f"%{q}%"))
        )
    rows = query.order_by(Apoteka.naziv.asc()).limit(limit).offset(offset).all()
    return [
        {"id": r.id, "naziv": r.naziv, "mejl": str(r.mejl), "adresa": r.adresa}
        for r in rows
    ]
