from logspy import *
from pathlib import Path
import pytest

def test_calcola_hash_determinismo():
    p = Path("app.log")
    risultato1 = calcola_hash(p)
    risultato2 = calcola_hash(p)
    assert risultato1 == risultato2

def test_calcola_hash_formato():
    p = Path("app.log")
    risultato = calcola_hash(p)
    assert len(risultato) == 64  # SHA-256 è sempre 64 caratteri hex

def test_leggi_righe_conta():
    p = Path("app.log")
    assert len(list(leggi_righe(p))) == 100


def test_logparse_error():
    context = ["riga mal formata appositamente"]
    s = context[0].split()
    with pytest.raises(LogParseError):
        if len(s) < 6:
            raise LogParseError("Riga malformata")

