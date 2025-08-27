from datetime import datetime, date
from sqlalchemy import BigInteger, Date, DateTime, Text, CheckConstraint, func
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

PHONE_RE = r'^[0-9+()\- ]{6,20}$'

class Korisnik(Base):
    __tablename__ = "korisnici"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ime: Mapped[str] = mapped_column(Text, nullable=False)
    prezime: Mapped[str] = mapped_column(Text, nullable=False)
    datum_rodjenja: Mapped[date] = mapped_column(Date, nullable=False)
    adresa: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False)
    broj_telefona: Mapped[str] = mapped_column(Text, nullable=False)
    sifra_hash: Mapped[str] = mapped_column(Text, nullable=False)



    __table_args__ = (CheckConstraint(f"broj_telefona ~ '{PHONE_RE}'", name="chk_broj_telefona"),)
    staratelji = relationship(
        "Staratelj",
        back_populates="korisnik",
        cascade="all, delete-orphan"
    )

    pretplate = relationship(
        "Pretplata",
        back_populates="korisnik",
        cascade="all, delete-orphan"
    )
