import fastapi
from logspy import *
from fastapi import *

app = FastAPI()

@app.get("/app.log")
def get_app_log():
    return "palleeeee"