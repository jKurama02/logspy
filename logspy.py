import functools
import sys
import argparse
import collections
from pathlib import Path
import time
import logging
from typing import Callable, Any
from dotenv import load_dotenv
import os
import asyncio
from datetime import date
from database import get_session, init_db
from sqlalchemy import select
from models import AnalisiLog
from services import analizza, calcola_hash
from tabulate import tabulate



def salva_analisi(risultato: dict) -> None:
    new_record = AnalisiLog(
          file_path=str(risultato["path"]),
          file_hash=calcola_hash(risultato["path"]),
          data_analisi=str(date.today()),
          totale_righe=risultato["totale"],
          n_errori=risultato["lvl"].get("ERROR", 0),
          n_warning=risultato["lvl"].get("WARNING", 0),
          n_info=risultato["lvl"].get("INFO", 0))
    with get_session() as session:
        session.add(new_record)
        session.commit()






load_dotenv()
LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
APP_NAME = os.getenv('APP_NAME', 'LogSpy')

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL), 
    format="%(asctime)s [%(levelname)s] %(message)s"
  )

# registra una mappatura tra il livello numerico e  una stringa di rappresentazione  ... fine 
logging.addLevelName(logging.DEBUG, f"\x1b[36mDEBUG\x1b[0m")
logging.addLevelName(logging.INFO, f"\x1b[32mINFO\x1b[0m")
logging.addLevelName(logging.WARNING, f"\x1b[33mWARNING\x1b[0m")
logging.addLevelName(logging.ERROR, f"\x1b[31mERROR\x1b[0m")
logging.addLevelName(logging.CRITICAL, f"\x1b[35mCRITICAL\x1b[0m")


def log_call(f) -> Callable[..., Any]:
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        status_c = f(*args)
        logging.debug(f"{f.__name__} chiamato con args=({args})")
        logging.debug(f"main ha restituito {status_c}")
    return wrapper

def timed(f) -> Callable[..., Any]: # Callable = tipo che rappresenta una funzione/chiamabile
    @functools.wraps(f)                                  # Any = qualsiasi tipo di valore
    def wrapper(*args, **kwargs):                                      
        logging.debug(f"--->Entro nel {f.__name__}")
        start = time.perf_counter()
        f(*args)
        end_t = time.perf_counter()
        logging.debug(f"--->Esco dal {f.__name__}")
        logging.debug(f"Tempo: {end_t-start:.2f} sec")
    return wrapper


# @log_call
# @timed
async def main_async(args: list[str]) -> None:
    parser = argparse.ArgumentParser(description=f'________{APP_NAME}__________')
    parser.add_argument('--files', required=True, nargs='+', help='file da analizzare')
    my_args = parser.parse_args(args)
    init_db() # e' idempotente
    paths = [Path(f) for f in my_args.files]
    for p in paths:
        if not p.exists():
            print(f"Errore: file '{p}' non trovato.")
            sys.exit(1)
    
    mapp = dict()   # ["app.log": "ASH", "paa.log":"ASH"]
    for a in paths:
        mapp[a] = calcola_hash(a)
    
    #pulizia del dict  mapp  da file gia' analizzati (if presente nel db , rimuovi dal dict mapp)
    with get_session() as session :           
        stmt = (select(AnalisiLog.file_hash))
        result = set(session.scalars(stmt))
        for p in paths:                         
            if mapp.get(p) in result: 
                mapp.pop(p)

    paths = [Path(f) for f in mapp.keys()]    # sovrascrive paths 

    risultati = await asyncio.gather(*[analizza(p) for p in paths]) #asyncio.gather(...) — prende tutte le coroutine, le avvolge in task, le lancia tutte insieme nell'event loop. Restituisce una coroutine che completa quando tutte le task sono finite.
    
    for r in risultati:
        salva_analisi(r);                                                                                                                  
        print(f"\nFile: {r['path']}  |  Righe totali: {r['totale']}\n")

        table = [["ERROR", r['lvl'].get('ERROR', 0)],["INFO", r['lvl'].get('INFO', 0)],["WARNING",  r['lvl'].get('WARNING', 0)]]
        print (tabulate(table,headers=["Level","Times"]))
        print(f"\nTop 5 messaggi di errore più frequenti:\n")
        for x, (msg, cnt) in enumerate(collections.Counter(r['msg']).most_common(5)):
            print(f"  {x+1}. {msg} (x{cnt})")
        print(f"SHA-256: {calcola_hash(r['path'])}")

if __name__ == "__main__":  # Memo: __name__ è una variabile speciale che vale "__main__" solo se il file viene eseguito direttamente; se il file è importato come modulo, assume il nome del file stesso. Usare if __name__ == "__main__": garantisce che il codice interno venga eseguito solo all'avvio diretto, proteggendo il modulo da esecuzioni accidentali durante l'importazione.
    asyncio.run(main_async(sys.argv[1:]))

#     asyncio.run(...)
#     1> crea un EVENT LOOP (il "motore" che gestisce le coroutine)
#     2> ci mette dentro main_async(...) come primo task
#     3> fa girare il loop finché main_async non finisce
#     4> chiude il loop e torna al mondo sync

#   main_async(sys.argv[1:]) da solo non esegue niente — restituisce solo un oggetto coroutine. È asyncio.run() che lo mette in moto.