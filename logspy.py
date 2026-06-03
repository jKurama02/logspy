import functools 
import sys
import argparse
import collections 
from pathlib import Path
import time
from dataclasses import dataclass 
from collections.abc import Generator
import hashlib
import logging
from typing import Callable, Any
from dotenv import load_dotenv
import os


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
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class LogParseError(Exception):
    pass
# non aggiunge comportamento, eredita dall'implementazione base: memorizza gli argomenti passati in .args e fornisce str che restituisce una rappresentazione leggibile basata su .args.

@dataclass
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


def leggi_righe(path: Path) -> Generator[str, None, None]:
    with open(path, "r") as file:      #with = Context managers
        for riga in file:
            yield riga


@log_call
@timed
def main(args: list[str]) -> None:
    parser = argparse.ArgumentParser(description=f'________{APP_NAME}__________')
    parser.add_argument('--file',required=True, help='file_to_search_logs')      # option that takes a value
    my_args = parser.parse_args(args)
    p = Path(my_args.file)
    if not p.exists():
        print(f"Errore: file '{my_args.file}' non trovato.")
        sys.exit(1)
    f = leggi_righe(p)
    d_lvl = dict()
    d_msg = dict()
    c = int()

    for l in f:
        c += 1
        s = l.split()
        try:
            if len(s) < 6:
                raise LogParseError(f"Riga malformata: '{l.strip()}'")
            msg = s[5:]
            gg = " ".join(msg)
            log = Log(f"{s[0]}:{s[1]}",s[2],s[3],gg)
            d_lvl[log.lvl] = d_lvl.get(log.lvl, 0) + 1
            if log.lvl == "ERROR":
                d_msg[log.msg] = d_msg.get(log.msg, 0) + 1
        except LogParseError as e:
            logging.warning(e)
        
    print(f"File: {my_args.file}  |  Righe totali: {c}\nERROR    : {d_lvl["ERROR"]}\nWARNING  : {d_lvl["WARNING"]}\nINFO     : {d_lvl["INFO"]}\n\nTop 5 messaggi di errore più frequenti:\n")
    for x,y in enumerate(collections.Counter(d_msg).most_common(5)):
        print(f"  {x+1}. {y[0]} (x{y[1]})")
    print(f"SHA-256: {calcola_hash(p)}")

if __name__ == "__main__":  # Memo: __name__ è una variabile speciale che vale "__main__" solo se il file viene eseguito direttamente; se il file è importato come modulo, assume il nome del file stesso. Usare if __name__ == "__main__": garantisce che il codice interno venga eseguito solo all'avvio diretto, proteggendo il modulo da esecuzioni accidentali durante l'importazione.
    main(sys.argv[1:])