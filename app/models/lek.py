from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Text, Boolean, Numeric, ForeignKey, CheckConstraint, UniqueConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Lek(Base):
    __tablename__ = "lekovi"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    id_apoteke: Mapped[int] = mapped_column(BigInteger, ForeignKey("apoteke.id", ondelete="CASCADE"), nullable=False)
    naziv: Mapped[str] = mapped_column(Text, nullable=False)
    dostupnost: Mapped[bool] = mapped_column(Boolean, nullable=False)
    cena: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    potreban_recept: Mapped[bool] = mapped_column(Boolean, nullable=False)



    __table_args__ = (
        UniqueConstraint("id_apoteke", "naziv", name="lek_unique_per_apoteka"),
        CheckConstraint("cena >= 0", name="chk_lek_cena_nonneg"),
        Index("idx_lekovi_apoteka", "id_apoteke", "naziv"),
    )

    apoteka = relationship("Apoteka", back_populates="lekovi")
    stavke = relationship("PretplataLek", back_populates="lek", cascade="all, delete-orphan")