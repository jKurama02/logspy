import functools 
import sys
import argparse
import collections 
from pathlib import Path
import time
from dataclasses import dataclass 
from collections.abc import  AsyncGenerator
import hashlib
import logging
from typing import Callable, Any
from dotenv import load_dotenv
import os
import aiofiles
import asyncio



#to_read = https://read.theaimerge.com/p/final-guide-on-parallel-processing#


load_dotenv()
LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
APP_NAME = os.getenv('APP_NAME', 'LogSpy')

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL), # vai nel modulo logging, cerca l'attributo che ha il nome scritto nella stringa LOG_LEVEL e dammi il suo valore 10/20/30/40/50
    format="%(asctime)s [%(levelname)s] %(message)s"
  )

# registra una mappatura tra il livello numerico e  una stringa di rappresentazione  ... fine 
logging.addLevelName(logging.DEBUG, f"\x1b[36mDEBUG\x1b[0m")
logging.addLevelName(logging.INFO, f"\x1b[32mINFO\x1b[0m")
logging.addLevelName(logging.WARNING, f"\x1b[33mWARNING\x1b[0m")
logging.addLevelName(logging.ERROR, f"\x1b[31mERROR\x1b[0m")
logging.addLevelName(logging.CRITICAL, f"\x1b[35mCRITICAL\x1b[0m")


def calcola_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):   #(walrus) assegna e valuta in una sola mossa
            h.update(chunk)
    return h.hexdigest()    #restituisce una stringa esadecimale di 64 caratteri 


class LogParseError(Exception):
    pass
# non aggiunge comportamento, eredita dall'implementazione base: memorizza gli argomenti passati in .args e fornisce str che restituisce una rappresentazione leggibile basata su .args.

@dataclass #genera automaticamente __init__, __repr__ e __eq__ basandosi sulle annotazioni di tipo
class Log():
    time_stamp: str
    lvl: str
    source: str
    msg: str
    def __str__(self):
        return(self.time_stamp + self.lvl + self.source + self.msg)
    
def log_call(f) -> Callable[..., Any]:
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        status_c = f(*args)
        logging.debug(f"{f.__name__} chiamato con args=({args})")   # logga dopo l'esecuzione
        logging.debug(f"main ha restituito {status_c}")             # logga dopo l'esecuzione
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


async def leggi_righe(path: Path) -> AsyncGenerator[str, None]:
    async with aiofiles.open(path, "r") as file:      #with = Context managers
        async for riga in file:
            yield riga


async def analizza(path: Path) -> dict:
    d_lvl: dict[str, int] = {}
    d_msg: dict[str, int] = {}
    c = 0

    async for l in leggi_righe(path):  #che internamente fa await a ogni riga
        c += 1
        s = l.split()
        try:
            if len(s) < 6:
                raise LogParseError(f"Riga malformata: '{l.strip()}'")
            gg = " ".join(s[5:])
            log = Log(f"{s[0]}:{s[1]}", s[2], s[3], gg)
            d_lvl[log.lvl] = d_lvl.get(log.lvl, 0) + 1
            if log.lvl == "ERROR":
                d_msg[log.msg] = d_msg.get(log.msg, 0) + 1
        except LogParseError as e:
            logging.warning(e)

    return {"path": path, "totale": c, "lvl": d_lvl, "msg": d_msg}



# @log_call
# @timed
async def main_async(args: list[str]) -> None:
    parser = argparse.ArgumentParser(description=f'________{APP_NAME}__________')
    parser.add_argument('--files', required=True, nargs='+', help='file/i da analizzare')  
    my_args = parser.parse_args(args)   #legge --files e ottiene la lista di path
    paths = [Path(f) for f in my_args.files]
    for p in paths:
        if not p.exists():
            print(f"Errore: file '{p}' non trovato.")
            sys.exit(1)

    risultati = await asyncio.gather(*[analizza(p) for p in paths]) #asyncio.gather(...) — prende tutte le coroutine, le avvolge in task, le lancia tutte insieme nell'event loop. Restituisce una coroutine che completa quando tutte sono finite.
    
    for r in risultati:
        print(f"\nFile: {r['path']}  |  Righe totali: {r['totale']}")
        print(f"ERROR    : {r['lvl'].get('ERROR', 0)}")
        print(f"WARNING  : {r['lvl'].get('WARNING', 0)}")
        print(f"INFO     : {r['lvl'].get('INFO', 0)}")
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