import hashlib
from pathlib import Path

def calcola_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:  # read-binary
        while chunk := f.read(8192): #
            h.update(chunk)
    return h.hexdigest()