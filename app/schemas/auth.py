from pydantic import BaseModel, EmailStr, constr

# --- Register ---
class RegisterKorisnik(BaseModel):
    ime: str
    prezime: str
    datum_rodjenja: str  # "YYYY-MM-DD"
    adresa: str
    email: EmailStr
    broj_telefona: constr(pattern=r'^[0-9+()\-\s]{6,20}$')
    lozinka: str

class RegisterAdmin(BaseModel):
    ime: str
    prezime: str
    email: EmailStr
    lozinka: str

class RegisterApoteka(BaseModel):
    naziv: str
    mejl: EmailStr
    adresa: str
    lozinka: str

class RegisterStaratelj(BaseModel):
    ime: str
    prezime: str
    email: EmailStr
    broj_telefona: constr(pattern=r'^[0-9+()\-\s]{6,20}$')
    id_korisnika: int
    dokument_starateljstva: str
    lozinka: str
    odobrio_admin: bool = False

# --- Login ---
class LoginKorisnik(BaseModel):
    email: EmailStr
    lozinka: str

class LoginAdmin(BaseModel):
    email: EmailStr
    lozinka: str

class LoginApoteka(BaseModel):
    mejl: EmailStr
    lozinka: str

class LoginStaratelj(BaseModel):
    email: EmailStr
    id_korisnika: int
    lozinka: str

# --- Token odgovor ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
