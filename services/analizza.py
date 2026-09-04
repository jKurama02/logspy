import logging
from collections.abc import AsyncGenerator
from pathlib import Path
import aiofiles

from schemas.log import Log, LogParseError


async def leggi_righe(path: Path) -> AsyncGenerator[str, None]:
    async with aiofiles.open(path, "r") as file:   
        async for riga in file:
            yield riga

async def analizza(path: Path) -> dict:
    d_lvl: dict[str, int] = {}
    d_msg: dict[str, int] = {}
    totale = 0

    async for l in leggi_righe(path):  #che internamente fa await a ogni riga
        totale += 1
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

    return {"path": path, "totale": totale, "lvl": d_lvl, "msg": d_msg}