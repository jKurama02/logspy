import bcrypt
from datetime import datetime, timedelta, timezone
from core.config import settings
from jose import jwt, JWTError

ALGORITHM = "HS256" #sarebbe piu' sicuro RS256, ma dato che dovra' supportare un elevato numero di requests scegliamo thi big boy

# bcrypt aggiunge caratteri alla password:str in modo da rendere obsolete le hash-table, rounds=10 costo del calcolo dell'hash stesso (evita/rallenta Brute Force)
def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=10))
    return hashed.decode("utf-8")

# ritorna il token decodicficato con i corrispettivi campi come sub e exp
def decode_access_token(token: str) -> dict:
    return jwt.decode(token,settings.secret_key, ALGORITHM)

def verify_password(plain: str, hashed: str) -> bool:
    return(bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8")))


def create_acces_token(sub:str, minutes:int | None = None) -> str:
    expire_minute = minutes if minutes is not None else settings.access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minute) #timedelta genera il tempo di delay (seconds,microseconds,milliseconds,minutes,hours,weeks)
    payload = {"sub": sub, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)




