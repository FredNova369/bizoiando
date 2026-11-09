from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.consultas import buscar_precos

app = FastAPI(title="Bizoiando - Onde Comprar")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def pagina_inicial():
    return FileResponse("static/index.html")


@app.get("/api/teste")
def teste():
    return {"mensagem": "A API do Bizoiando está funcionando!"}

@app.get("/api/buscar")
def buscar(q: str = Query(..., min_length=1, description="Nome do perecível")):
    resultados = buscar_precos(q.strip())
    return {"busca": q, "total": len(resultados), "resultados": resultados}