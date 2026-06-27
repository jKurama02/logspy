from fastapi import FastAPI
from pydantic import BaseModel



class RisultatoAnalisi(BaseModel):     #FastAPI chiama .model_dump() sull'oggetto Pydantic e lo serializza in JSON
      file_path:    str
      file_hash:    str
      data_analisi: str
      totale_righe: int 
      n_errori:     int 
      n_warning:    int 
      n_info:       int 

app = FastAPI()

r = RisultatoAnalisi(
      id = 1,
      file_path=    "/thisisiapath",
      file_hash=    "thisisahash",
      data_analisi= "2026",
      totale_righe= 56 ,
      n_errori=     4 ,
      n_warning=    5 ,
      n_info=       6 )
@app.get("/test", response_model=RisultatoAnalisi)
async def root():
      return r