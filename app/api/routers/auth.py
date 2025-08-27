from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2._psycopg import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import (
    RegisterKorisnik, RegisterAdmin, RegisterApoteka, RegisterStaratelj,
    LoginKorisnik, LoginAdmin, LoginApoteka, LoginStaratelj, Token
)
from app.models.korisnik import Korisnik
from app.models.admin import Administrator
from app.models.apoteka import Apoteka
from app.models.staratelj import Staratelj

router = APIRouter(prefix="/auth", tags=["Auth"])

# ---------- REGISTER ----------
@router.post("/register/korisnik", response_model=Token, status_code=201)
def register_korisnik(payload: RegisterKorisnik, db: Session = Depends(get_db)):
    if db.query(Korisnik).filter(Korisnik.email == payload.email).first():
        raise HTTPException(400, "Email je već zauzet.")
    obj = Korisnik(
        ime=payload.ime, prezime=payload.prezime,
        datum_rodjenja=payload.datum_rodjenja, adresa=payload.adresa,
        email=payload.email, broj_telefona=payload.broj_telefona,
        sifra_hash=get_password_hash(payload.lozinka),
    )
    db.add(obj); db.commit(); db.refresh(obj)
    token = create_access_token({"sub": obj.email, "type": "korisnik", "id": obj.id})
    return Token(access_token=token)

@router.post("/register/admin", response_model=Token, status_code=201)
def register_admin(payload: RegisterAdmin, db: Session = Depends(get_db)):
    if db.query(Administrator).filter(Administrator.email == payload.email).first():
        raise HTTPException(400, "Email je već zauzet.")
    obj = Administrator(
        ime=payload.ime, prezime=payload.prezime,
        email=payload.email, sifra_hash=get_password_hash(payload.lozinka),
    )
    db.add(obj); db.commit(); db.refresh(obj)
    token = create_access_token({"sub": obj.email, "type": "admin", "id": obj.id})
    return Token(access_token=token)

@router.post("/register/apoteka", response_model=Token, status_code=201)
def register_apoteka(payload: RegisterApoteka, db: Session = Depends(get_db)):
    if db.query(Apoteka).filter(Apoteka.mejl == payload.mejl).first():
        raise HTTPException(400, "Mejl je već zauzet.")
    obj = Apoteka(
        naziv=payload.naziv, mejl=payload.mejl, adresa=payload.adresa,
        sifra_hash=get_password_hash(payload.lozinka),
    )
    db.add(obj); db.commit(); db.refresh(obj)
    token = create_access_token({"sub": obj.mejl, "type": "apoteka", "id": obj.id})
    return Token(access_token=token)

@router.post("/register/staratelj", response_model=Token, status_code=201)
def register_staratelj(payload: RegisterStaratelj, db: Session = Depends(get_db)):
    # 1) FK korisnika
    exists_user = db.query(Korisnik.id).filter(Korisnik.id == payload.id_korisnika).first()
    if not exists_user:
        raise HTTPException(status_code=400, detail="Povezani korisnik ne postoji.")

    # 2) Meka provera: korisnik već ima staratelja?
    already = db.query(Staratelj.id).filter(Staratelj.id_korisnika == payload.id_korisnika).first()
    if already:
        raise HTTPException(status_code=400, detail="Korisnik već ima staratelja.")

    # (opciono) jedinstven email globalno ili po korisniku – po želji
    # if db.query(Staratelj.id).filter(Staratelj.email == payload.email).first():
    #     raise HTTPException(status_code=400, detail="Staratelj sa ovim email-om već postoji.")

    obj = Staratelj(
        ime=payload.ime,
        prezime=payload.prezime,
        email=payload.email,
        broj_telefona=payload.broj_telefona,
        id_korisnika=payload.id_korisnika,
        dokument_starateljstva=payload.dokument_starateljstva,
        odobrio_admin=getattr(payload, "odobrio_admin", False),
        sifra_hash=get_password_hash(payload.lozinka),
    )

    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # ako postoji UNIQUE indeks na staratelji(id_korisnika), ovde ga hvatamo
        raise HTTPException(status_code=400, detail="Korisnik već ima staratelja.")
    db.refresh(obj)

    token = create_access_token({
        "sub": obj.email,
        "type": "staratelj",
        "id": obj.id,
        "id_korisnika": obj.id_korisnika
    })
    return Token(access_token=token)

# ---------- LOGIN ----------
@router.post("/login/korisnik", response_model=Token)
def login_korisnik(payload: LoginKorisnik, db: Session = Depends(get_db)):
    obj = db.query(Korisnik).filter(Korisnik.email == payload.email).first()
    if not obj or not verify_password(payload.lozinka, obj.sifra_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Pogrešan email ili lozinka.")
    token = create_access_token({"sub": obj.email, "type": "korisnik", "id": obj.id})
    return Token(access_token=token)

@router.post("/login/admin", response_model=Token)
def login_admin(payload: LoginAdmin, db: Session = Depends(get_db)):
    obj = db.query(Administrator).filter(Administrator.email == payload.email).first()
    if not obj or not verify_password(payload.lozinka, obj.sifra_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Pogrešan email ili lozinka.")
    token = create_access_token({"sub": obj.email, "type": "admin", "id": obj.id})
    return Token(access_token=token)

@router.post("/login/apoteka", response_model=Token)
def login_apoteka(payload: LoginApoteka, db: Session = Depends(get_db)):
    obj = db.query(Apoteka).filter(Apoteka.mejl == payload.mejl).first()
    if not obj or not verify_password(payload.lozinka, obj.sifra_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Pogrešan email ili lozinka.")
    token = create_access_token({"sub": obj.mejl, "type": "apoteka", "id": obj.id})
    return Token(access_token=token)

@router.post("/login/staratelj", response_model=Token)
def login_staratelj(payload: LoginStaratelj, db: Session = Depends(get_db)):
    obj = db.query(Staratelj).filter(
        Staratelj.email == payload.email,
        Staratelj.id_korisnika == payload.id_korisnika
    ).first()
    if not obj or not verify_password(payload.lozinka, obj.sifra_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Pogrešan email/korisnik ili lozinka.")
    token = create_access_token({"sub": obj.email, "type": "staratelj", "id": obj.id, "id_korisnika": obj.id_korisnika})
    return Token(access_token=token)
