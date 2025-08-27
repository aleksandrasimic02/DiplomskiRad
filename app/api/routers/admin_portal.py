from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth_deps import get_current_admin
from app.models.admin import Administrator
from app.models.staratelj import Staratelj
from app.schemas.staratelj import StarateljAdminListOut
from sqlalchemy import or_

router = APIRouter(prefix="/admin", tags=["Admin portal"])

class ApproveStarateljIn(BaseModel):
    staratelj_id: int

@router.post("/odobriNalog")
def odobri_nalog(payload: ApproveStarateljIn,
                 admin: Administrator = Depends(get_current_admin),
                 db: Session = Depends(get_db)):
    st = db.query(Staratelj).filter(Staratelj.id == payload.staratelj_id).first()
    if not st:
        raise HTTPException(status_code=404, detail="Staratelj ne postoji.")
    if st.odobrio_admin:
        return {"message": "Nalog je već odobren."}
    st.odobrio_admin = True
    db.commit()
    return {"message": "Nalog staratelja odobren.", "staratelj_id": st.id}

@router.delete("/obrisiNalog", status_code=204)
def obrisi_sopstveni_admin_nalog(admin: Administrator = Depends(get_current_admin),
                                 db: Session = Depends(get_db)):
    db.delete(admin)
    db.commit()
    return

@router.get("/staratelji/neodobreni", response_model=list[StarateljAdminListOut])
def list_neodobreni_staratelji(
    db: Session = Depends(get_db),
    _admin = Depends(get_current_admin),  # samo proveri da je admin
):
    # hvata i False i NULL (ako je kolona nullable)
    q = (
        db.query(Staratelj)
        .filter(or_(Staratelj.odobrio_admin.is_(False), Staratelj.odobrio_admin.is_(None)))
        .order_by(Staratelj.id.desc())
    )
    return q.all()