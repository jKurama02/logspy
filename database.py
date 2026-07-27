from typing import Generator, final
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models import Base

engine = create_engine("sqlite:///logspy.db", connect_args={"check_same_thread": False})  #sqlite di default vieta di usare la stessa connessione da un thread diverso da quello che l'ha aperta

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    Base.metadata.create_all(engine)

def get_session() -> Session:  # per CLI
    return Session(engine)  #apre connessioni tramite lo stesso engine e permette di leggere/scrivere le righe usando gli oggetti AnalisiLog

def get_db(): #dependency per FastAPI
    db = SessionLocal()    
    try:
        yield db
    finally:
        db.close()