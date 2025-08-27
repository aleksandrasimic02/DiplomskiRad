from pydantic import BaseModel, EmailStr, constr
from datetime import date
from .common import PHONE_RE

class KorisnikCreate(BaseModel):
    ime: str
    prezime: str
    datum_rodjenja: date
    adresa: str
    email: EmailStr
    broj_telefona: constr(pattern=PHONE_RE)
    sifra_hash: str  # očekujemo hash

class KorisnikOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True
