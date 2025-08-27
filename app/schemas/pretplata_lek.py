from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict as ConfigDict

class PretplataLekCreate(BaseModel):
    id_pretplate: int           # ili pretplata_id, uskladi sa modelom
    id_leka: int
    recept_dokument: str | None = Field(default=None, alias="recept")  # ⬅️ prihvati oba naziva
    model_config = ConfigDict(populate_by_name=True)

class PretplataLekOut(BaseModel):
    id: int
    class Config:
        from_attributes = True
