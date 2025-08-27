from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Administrator(Base):
    __tablename__ = "administratori"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ime: Mapped[str] = mapped_column(Text, nullable=False)
    prezime: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False)
    sifra_hash: Mapped[str] = mapped_column(Text, nullable=False)


