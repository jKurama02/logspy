from sqlalchemy import create_engine
from sqlalchemy.orm import  Session
from models import Base

engine = create_engine("sqlite:///logspy.db", echo=True)

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    return Session(engine)