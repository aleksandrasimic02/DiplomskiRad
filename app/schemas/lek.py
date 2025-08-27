from pydantic import BaseModel, Field

class LekCreate(BaseModel):
    id_apoteke: int
    naziv: str
    dostupnost: bool = True
    cena: float = Field(ge=0)
    potreban_recept: bool = False

class LekOut(BaseModel):
    id: int
    naziv: str
    class Config:
        from_attributes = True
