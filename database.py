from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base

engine = create_engine("sqlite:///logspy.db")

def init_db() -> None:
    Base.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)  #apre connessioni tramite lo stesso engine e permette di leggere/scrivere le righe usando gli oggetti AnalisiLog

