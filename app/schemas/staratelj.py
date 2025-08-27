from pydantic import BaseModel, EmailStr, constr
from .common import PHONE_RE

class StarateljCreate(BaseModel):
    ime: str
    prezime: str
    email: EmailStr
    broj_telefona: constr(pattern=PHONE_RE)
    id_korisnika: int
    dokument_starateljstva: str
    odobrio_admin_id: int | None = None  # neobavezna veza -> nullable

class StarateljOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class StarateljAdminListOut(BaseModel):
    id: int
    ime: str
    prezime: str
    email: EmailStr
    broj_telefona: str
    id_korisnika: int
    dokument_starateljstva: str | None = None
    odobrio_admin: bool | None = None