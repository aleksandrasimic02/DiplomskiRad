from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.korisnik import Korisnik
from app.models.apoteka import Apoteka
from app.models.staratelj import Staratelj
from app.models.admin import Administrator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # samo radi ekstrakcije Bearer tokena

class TokenPayload(BaseModel):
    sub: str
    type: str
    id: int
    id_korisnika: Optional[int] = None
    # exp polje postoji u JWT-u, ali nam nije neophodno za validaciju ovde

def _decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nevalidan ili istekao token.")

def get_current_korisnik(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Korisnik:
    data = _decode_token(token)
    if data.type != "korisnik":
        raise HTTPException(status_code=403, detail="Zabranjen pristup (nije korisnik).")
    obj = db.query(Korisnik).filter(Korisnik.id == data.id).first()
    if not obj:
        raise HTTPException(status_code=401, detail="Korisnik ne postoji.")
    return obj

def get_current_apoteka(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Apoteka:
    data = _decode_token(token)
    if data.type != "apoteka":
        raise HTTPException(status_code=403, detail="Zabranjen pristup (nije apoteka).")
    obj = db.query(Apoteka).filter(Apoteka.id == data.id).first()
    if not obj:
        raise HTTPException(status_code=401, detail="Apoteka ne postoji.")
    return obj

def get_current_staratelj(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Staratelj:
    data = _decode_token(token)
    if data.type != "staratelj":
        raise HTTPException(status_code=403, detail="Zabranjen pristup (nije staratelj).")
    obj = db.query(Staratelj).filter(Staratelj.id == data.id).first()
    if not obj:
        raise HTTPException(status_code=401, detail="Staratelj ne postoji.")
    # (opciono) dodatna provera da je token id_korisnika usklađen sa zapisom:
    if data.id_korisnika is not None and obj.id_korisnika != data.id_korisnika:
        raise HTTPException(status_code=401, detail="Nevalidan token (ne odgovara korisniku).")
    return obj

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Administrator:
    data = _decode_token(token)
    if data.type != "admin":
        raise HTTPException(status_code=403, detail="Zabranjen pristup (nije admin).")
    obj = db.query(Administrator).filter(Administrator.id == data.id).first()
    if not obj:
        raise HTTPException(status_code=401, detail="Admin ne postoji.")
    return obj

def get_korisnik_id_from_korisnik_or_staratelj(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> int:
    data = _decode_token(token)
    if data.type == "korisnik":
        return data.id
    if data.type == "staratelj":
        # osnovna verifikacija: staratelj postoji i token nosi id_korisnika
        st = db.query(Staratelj).filter(Staratelj.id == data.id).first()
        if not st or (data.id_korisnika is not None and st.id_korisnika != data.id_korisnika):
            raise HTTPException(status_code=401, detail="Nevalidan staratelj token.")
        return st.id_korisnika
    raise HTTPException(status_code=403, detail="Potrebno je da budeš korisnik ili staratelj.")


# app/core/auth_deps.py
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/korisnik")  # ili tvoj tokenUrl


def get_pretplate_owner_id(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> int:
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nevažeći token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise creds_exc

    utype = payload.get("type")

    # ---- KORISNIK ----
    if utype == "korisnik":
        # preferiraj eksplicitne ID claim-ove
        for key in ("korisnik_id", "user_id", "id"):
            v = payload.get(key)
            if v is not None:
                try:
                    return int(v)
                except (TypeError, ValueError):
                    pass

        sub = payload.get("sub") or payload.get("email")
        if sub is None:
            raise creds_exc

        if isinstance(sub, int) or (isinstance(sub, str) and sub.isdigit()):
            return int(sub)

        # sub je email → pronađi korisnika po emailu
        k = db.query(Korisnik).filter(Korisnik.email == sub).first()
        if not k:
            raise creds_exc
        return k.id

    # ---- STARATELJ ----
    if utype == "staratelj":
        target = payload.get("id_korisnika")
        if target is not None:
            if isinstance(target, int) or (isinstance(target, str) and target.isdigit()):
                return int(target)
            # email u claim-u
            k = db.query(Korisnik).filter(Korisnik.email == target).first()
            if not k:
                raise creds_exc
            return k.id

        # fallback: saznaj staratelja pa njegovog korisnika
        sid = payload.get("staratelj_id") or payload.get("id")
        if sid is not None and (isinstance(sid, int) or (isinstance(sid, str) and sid.isdigit())):
            st = db.get(Staratelj, int(sid)) if hasattr(db, "get") else db.query(Staratelj).get(int(sid))  # SQLA 1.x/2.x
            if st:
                return st.id_korisnika

        sub = payload.get("sub") or payload.get("email")
        if sub:
            st = db.query(Staratelj).filter(Staratelj.email == sub).first()
            if st:
                return st.id_korisnika

        raise creds_exc

    # druge uloge nemaju pristup ovoj logici
    raise HTTPException(status_code=403, detail="Samo korisnik ili staratelj imaju pristup.")
