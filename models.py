import time
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass

class AnalisiLog(Base):
    __tablename__ = "analisi_log"

    id:           Mapped[int] = mapped_column(primary_key=True)
    owner_id:     Mapped[int] = mapped_column()
    owner:        Mapped["User | None"] = relationship(back_populates="analisi")
    file_path:    Mapped[str] = mapped_column(String, nullable=False) 
    file_hash:    Mapped[str] = mapped_column(String, nullable=False)
    data_analisi: Mapped[str] = mapped_column(String, nullable=False)
    totale_righe: Mapped[int] = mapped_column(Integer, nullable=False)
    n_errori:     Mapped[int] = mapped_column(Integer, nullable=False)
    n_warning:    Mapped[int] = mapped_column(Integer, nullable=False)
    n_info:       Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self):
        return f"AnalisiLog(file={self.file_path}, errori={self.n_errori}, data={self.data_analisi})"


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(primary_key=True)
    username:        Mapped[str]      = mapped_column(String(50), unique=True, index=True)
    email:           Mapped[str]      = mapped_column(String, unique=True , nullable=False, index=True)
    hashed_password: Mapped[str]      = mapped_column(String, nullable=False)
    created_at:      Mapped[datetime] = mapped_column(default=lambda:datetime.now(timezone.utc))

    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"