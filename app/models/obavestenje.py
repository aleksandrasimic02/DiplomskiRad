from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, UniqueConstraint, func, Index
)
from sqlalchemy.orm import relationship
from app.db.base import Base

class Obavestenje(Base):
    __tablename__ = "obavestenja"
    id = Column(Integer, primary_key=True, index=True)
    naziv = Column(String(160), nullable=False)
    opis = Column(Text, nullable=False)

    # opcione veze za lakši ORM pristup (ne moraju ti ako ne koristiš)
    admini = relationship("ObavestenjeAdmin", back_populates="obavestenje", cascade="all, delete-orphan")
    korisnici = relationship("ObavestenjeKorisnik", back_populates="obavestenje", cascade="all, delete-orphan")
    apoteke = relationship("ObavestenjeApoteka", back_populates="obavestenje", cascade="all, delete-orphan")


class ObavestenjeAdmin(Base):
    __tablename__ = "obavestenja_admini"
    id = Column(Integer, primary_key=True, index=True)
    obavestenje_id = Column(Integer, ForeignKey("obavestenja.id", ondelete="CASCADE"), nullable=False)
    admin_id = Column(Integer, ForeignKey("administratori.id", ondelete="CASCADE"), nullable=False)

    procitano = Column(Boolean, nullable=False, server_default="false")

    obavestenje = relationship("Obavestenje", back_populates="admini")
    __table_args__ = (
        UniqueConstraint("obavestenje_id", "admin_id", name="uq_obav_admin"),
        Index("ix_obav_admin_lookup", "admin_id", "obavestenje_id"),
    )


class ObavestenjeKorisnik(Base):
    __tablename__ = "obavestenja_korisnici"
    id = Column(Integer, primary_key=True, index=True)
    obavestenje_id = Column(Integer, ForeignKey("obavestenja.id", ondelete="CASCADE"), nullable=False)
    korisnik_id = Column(Integer, ForeignKey("korisnici.id", ondelete="CASCADE"), nullable=False)

    procitano = Column(Boolean, nullable=False, server_default="false")

    obavestenje = relationship("Obavestenje", back_populates="korisnici")
    __table_args__ = (
        UniqueConstraint("obavestenje_id", "korisnik_id", name="uq_obav_korisnik"),
        Index("ix_obav_korisnik_lookup", "korisnik_id", "obavestenje_id"),
    )


class ObavestenjeApoteka(Base):
    __tablename__ = "obavestenja_apoteke"
    id = Column(Integer, primary_key=True, index=True)
    obavestenje_id = Column(Integer, ForeignKey("obavestenja.id", ondelete="CASCADE"), nullable=False)
    apoteka_id = Column(Integer, ForeignKey("apoteke.id", ondelete="CASCADE"), nullable=False)

    procitano = Column(Boolean, nullable=False, server_default="false")

    obavestenje = relationship("Obavestenje", back_populates="apoteke")
    __table_args__ = (
        UniqueConstraint("obavestenje_id", "apoteka_id", name="uq_obav_apoteka"),
        Index("ix_obav_apoteka_lookup", "apoteka_id", "obavestenje_id"),
    )
