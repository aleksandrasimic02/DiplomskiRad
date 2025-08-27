from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Text, ForeignKey, CheckConstraint, UniqueConstraint, Boolean, func
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from .korisnik import PHONE_RE

class Staratelj(Base):
    __tablename__ = "staratelji"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ime: Mapped[str] = mapped_column(Text, nullable=False)
    prezime: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(CITEXT, nullable=False)
    broj_telefona: Mapped[str] = mapped_column(Text, nullable=False)
    id_korisnika: Mapped[int] = mapped_column(BigInteger, ForeignKey("korisnici.id", ondelete="CASCADE"), nullable=False)
    dokument_starateljstva: Mapped[str] = mapped_column(Text, nullable=False)
    sifra_hash: Mapped[str] = mapped_column(Text, nullable=False)  # <—
    # umesto FK na administratore → običan boolean flag
    odobrio_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")


    korisnik = relationship("Korisnik", back_populates="staratelji")

    __table_args__ = (
        UniqueConstraint("id_korisnika", "email", name="staratelj_email_unique_per_user"),
        CheckConstraint(f"broj_telefona ~ '{PHONE_RE}'", name="chk_broj_telefona_st"),
    )

