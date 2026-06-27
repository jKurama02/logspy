from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class AnalisiLog(Base):
    __tablename__ = "analisilog"

    id:           Mapped[int] = mapped_column(primary_key=True)
    file_path:    Mapped[str] = mapped_column(String)
    file_hash:    Mapped[str] = mapped_column(String)
    data_analisi: Mapped[str] = mapped_column(String)
    totale_righe: Mapped[int] = mapped_column(Integer)
    n_errori:     Mapped[int] = mapped_column(Integer)
    n_warning:    Mapped[int] = mapped_column(Integer)
    n_info:       Mapped[int] = mapped_column(Integer)

    def __repr__(self):
        return f"AnalisiLog(file={self.file_path}, data={self.data_analisi}, errori={self.n_errori})"
