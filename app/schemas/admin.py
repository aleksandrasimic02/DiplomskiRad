from pydantic import BaseModel, EmailStr

class AdminCreate(BaseModel):
    ime: str
    prezime: str
    email: EmailStr
    sifra_hash: str
    id_staratelja: int | None = None  # neobavezna veza -> nullable

class AdminOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True
