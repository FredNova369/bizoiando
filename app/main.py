from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Bizoiando - Onde Comprar")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def pagina_inicial():
    return FileResponse("static/index.html")


@app.get("/api/teste")
def teste():
    return {"mensagem": "A API do Bizoiando está funcionando!"}