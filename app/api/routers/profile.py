from fastapi import APIRouter, Depends
from app.core.auth_deps import get_current_apoteka, get_current_korisnik, get_current_staratelj
from app.models.apoteka import Apoteka
from app.models.korisnik import Korisnik
from app.models.staratelj import Staratelj

router = APIRouter(prefix="/profil", tags=["Profil"])

@router.get("/apoteka")
def profil_apoteka(apoteka: Apoteka = Depends(get_current_apoteka)):
    return {
        "id": apoteka.id,
        "naziv": apoteka.naziv,
        "mejl": str(apoteka.mejl),
        "adresa": apoteka.adresa,
    }

@router.get("/korisnik")
def profil_korisnik(korisnik: Korisnik = Depends(get_current_korisnik)):
    return {
        "id": korisnik.id,
        "ime": korisnik.ime,
        "prezime": korisnik.prezime,
        "email": str(korisnik.email),
        "adresa": korisnik.adresa,
        "datum_rodjenja": str(korisnik.datum_rodjenja),
        "broj_telefona": korisnik.broj_telefona,
    }

@router.get("/staratelj")
def profil_staratelj(staratelj: Staratelj = Depends(get_current_staratelj)):
    return {
        "id": staratelj.id,
        "ime": staratelj.ime,
        "prezime": staratelj.prezime,
        "email": str(staratelj.email),
        "broj_telefona": staratelj.broj_telefona,
        "id_korisnika": staratelj.id_korisnika,
        "odobrio_admin": staratelj.odobrio_admin,
        "dokument_starateljstva": staratelj.dokument_starateljstva,
    }
