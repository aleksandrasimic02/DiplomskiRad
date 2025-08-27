from datetime import datetime, date
from sqlalchemy import BigInteger, DateTime, Date, Text, Boolean, Integer, ForeignKey, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Pretplata(Base):
    __tablename__ = "pretplate"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    id_korisnika: Mapped[int] = mapped_column(BigInteger, ForeignKey("korisnici.id", ondelete="CASCADE"), nullable=False)
    datum_pocetka: Mapped[date] = mapped_column(Date, nullable=False)
    dan_u_mesecu_dostave: Mapped[int] = mapped_column(Integer, nullable=False)
    naziv: Mapped[str] = mapped_column(Text, nullable=False)
    aktivna: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)



    __table_args__ = (
        CheckConstraint("dan_u_mesecu_dostave BETWEEN 1 AND 28", name="chk_dan_u_mesecu"),
        Index("idx_pretplate_korisnik", "id_korisnika"),
    )

    korisnik = relationship("Korisnik", back_populates="pretplate")
    stavke = relationship("PretplataLek", back_populates="pretplata", cascade="all, delete-orphan")
