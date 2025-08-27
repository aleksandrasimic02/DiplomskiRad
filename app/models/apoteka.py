from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Text, Index, func
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Apoteka(Base):
    __tablename__ = "apoteke"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    naziv: Mapped[str] = mapped_column(Text, nullable=False)
    mejl: Mapped[str] = mapped_column(CITEXT, nullable=False, unique=True)
    adresa: Mapped[str] = mapped_column(Text, nullable=False)
    sifra_hash: Mapped[str] = mapped_column(Text, nullable=False)  # <—
    lekovi = relationship("Lek", back_populates="apoteka", cascade="all, delete-orphan")

