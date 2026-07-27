from fastapi import FastAPI, HTTPException
from sqlalchemy import true
from core.config import settings
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from services import security

app = FastAPI(title=settings.app_name, version="0.5.0", description = "BOMBOKLATT")

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)

class UserRead(BaseModel):        # ESCE verso il client
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True, frozen=True)


@app.post("/auth/register", response_model=UserRead)
def register(user: UserCreate):
    finto_utente_dal_db = {
        "id":1,
        "username" : user.username,
        "email": user.email,
        "hashed_password": "FINTA_HASH_SEGRETA_123"
    }
    return finto_utente_dal_db

class HealthResponse(BaseModel):
    log_id: int
    livello: str


@app.get("/health/{log_id}", response_model=HealthResponse, responses={404: {"description": "Log non trovato"},},)
def health(log_id:int, livello:str="ERROR"):
    if log_id > 50:
        raise HTTPException(status_code=404, detail="Log non trovato")
    return {"log_id" : log_id , "livello" : livello}


@app.get("/hash_test/{s}")
def get_salt(s:str):
    a = security.hash_password(s)
    return(security.verify_password(s, a))

@app.get("/create_token/{s}")
def create_token(s:str, m:int = 10):
    return security.create_acces_token(s, m)

@app.get("/decode_token/{s}")
def decode_token(s:str):
    return security.decode_access_token(s)







from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, FastAPI

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}