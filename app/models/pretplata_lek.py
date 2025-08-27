from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Text, ForeignKey, UniqueConstraint, Index, func, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class PretplataLek(Base):
    __tablename__ = "pretplata_lek"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    id_pretplate: Mapped[int] = mapped_column(BigInteger, ForeignKey("pretplate.id", ondelete="CASCADE"), nullable=False)
    id_leka: Mapped[int] = mapped_column(BigInteger, ForeignKey("lekovi.id", ondelete="CASCADE"), nullable=False)
    recept_dokument: Mapped[str | None] = mapped_column(Text, nullable=True)  # neobavezno polje
    odobreno_apoteka: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))



    __table_args__ = (
        UniqueConstraint("id_pretplate", "id_leka", name="pretplata_lek_unique"),
        Index("idx_pretplata_lek_pretplata", "id_pretplate"),
        Index("idx_pretplata_lek_lek", "id_leka"),
    )

    pretplata = relationship("Pretplata", back_populates="stavke")
    lek = relationship("Lek", back_populates="stavke")
