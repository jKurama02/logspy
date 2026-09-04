from ctypes import sizeof
from fileinput import filename
from logging import info
from os import name
from pydoc import describe
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, Body, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from core.config import settings
from pydantic import BaseModel, EmailStr, Field, ConfigDict
import database
from models import User
from services import analizza, security
from schemas.user import UserCreate, UserRead
from services.security import hash_password
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from jose import JWTError, jwt
from fastapi.responses import HTMLResponse, JSONResponse




app = FastAPI(title=settings.app_name, version="0.5.0", description = "Anmedyns first WebServer")
# Instrumentator().instrument(app).expose(app)


# @app.get("/", response_class=HTMLResponse)
# def login_page():
#     return """
#     <input id="u" placeholder="username">
#     <input id="p" type="password" placeholder="password">
#     <button onclick="login()">Login</button>
#     <pre id="out"></pre>
#     <script>
#       async function login() {
#         const body = new URLSearchParams({ username: u.value, password: p.value });
#         const r = await fetch("/token", { method: "POST", body });
#         if (!r.ok) { out.textContent = "Login fallito"; return; }
#         const t = (await r.json()).access_token;
#         const logs = await fetch("/logs", { headers: { Authorization: "Bearer " + t } });
#         out.textContent = await logs.text();
#       }
#     </script>
#     """

# @app.get("/create_token/{s}")
# def create_token(s:str, m:int = 30):
#     return security.create_acces_token(s, m)

# @app.get("/decode_token/{s}")
# def decode_token(s:str):
#     return security.decode_access_token(s)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/auth/register", response_model=UserRead, responses={201: {"description": "User registered"},},)
def register(user: UserCreate, db : Session = Depends(database.get_db)):
    new_user = User(
        username = user.username,
        email = user.email,
        hashed_password = hash_password(user.password)
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback() 
        raise HTTPException(status_code=409,detail="Username or email already present")
    db.refresh(new_user)
    return new_user


@app.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db : Session = Depends(database.get_db)):
    user = db.scalar(select(User).where(User.username == form_data.username))
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"access_token": security.create_acces_token(user.username,15), "token_type": "bearer"}

# --- VALIDAZIONE TOKEN (eseguita ad ogni richiesta su endpoint protetti) ---
def get_current_user( token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> User:
    credentials_exception = HTTPException(401, "Token not valid")
    try:
        payload = security.decode_access_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise credentials_exception
    return user

# --- ENDPOINT PROTETTO DI ESEMPIO ---
# @app.get("/me")
# def list_logs(current_user: User = Depends(get_current_user)):
#     return current_user


import hashlib 

@app.post("/logs/upload")
async def create_upload_file(file: UploadFile,current_user: User = Depends(get_current_user)):
    h = hashlib.sha256()
    with open(f"./tmp/{file.filename}", "wb") as f:
        while chunk := await file.read(8192): 
            f.write(chunk)
            h.update(chunk)
        
    headers = {"X-Cache-Status": "HIT"}
    return JSONResponse(content={"hash": h.hexdigest(), "user": current_user.username} , headers=headers)



    # contenuto = await file.read()
    # return {
    #     "nome file": file.filename,
    #     "dimensione":  len(contenuto),
    #     "descrizione": descrizione,
    #     "terzo parameto": palleculo
    # }

    #return {"filename": file.filename}
