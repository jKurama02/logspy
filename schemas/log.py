from dataclasses import dataclass


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
