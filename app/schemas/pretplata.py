from pydantic import BaseModel, conint, ConfigDict
from datetime import date

class PretplataCreate(BaseModel):
    # id_korisnika: int
    dan_u_mesecu_dostave: conint(ge=1, le=28)
    naziv: str
    datum_pocetka: date | None = None
    aktivna: bool = True

class PretplataOut(BaseModel):
    id: int
    naziv: str
    class Config:
        from_attributes = True

class PretplataApproveIn(BaseModel):
    pretplata_id: int

class PretplataApproveOut(BaseModel):
    pretplata_id: int
    updated_items: int
    aktivna: bool
    model_config = ConfigDict(from_attributes=True)