from pydantic import BaseModel, EmailStr

class ApotekaCreate(BaseModel):
    naziv: str
    mejl: EmailStr
    adresa: str

class ApotekaOut(BaseModel):
    id: int
    mejl: EmailStr
    class Config:
        from_attributes = True
