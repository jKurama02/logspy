from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db
from models import User
from services.security import decode_access_token

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
# OAuth2PasswordBearer è una classe di FastAPI che implementa lo schema di sicurezza OAuth2 "password flow" con Bearer token. Istanziandola ottieni un dependency callable: una funzione-dipendenza che estrae il token dall'header Authorization: Bearer <token>





