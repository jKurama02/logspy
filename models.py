from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer

class Base(DeclarativeBase):
    pass

class AnalisiLog(Base):
    __tablename__ = "analisi_log"

    id:           Mapped[int] = mapped_column(primary_key=True)
    file_path:    Mapped[str] = mapped_column(String, nullable=False)
    file_hash:    Mapped[str] = mapped_column(String, nullable=False)
    data_analisi: Mapped[str] = mapped_column(String, nullable=False)
    totale_righe: Mapped[int] = mapped_column(Integer, nullable=False)
    n_errori:     Mapped[int] = mapped_column(Integer, nullable=False)
    n_warning:    Mapped[int] = mapped_column(Integer, nullable=False)
    n_info:       Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self):
        return f"AnalisiLog(file={self.file_path}, errori={self.n_errori}, data={self.data_analisi})"

