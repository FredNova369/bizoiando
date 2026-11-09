from datetime import date

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.consultas import (
    buscar_precos,
    importar_csv,
    inserir_preco,
    listar_mercados,
    listar_produtos,
)

app = FastAPI(title="Bizoiando - Onde Comprar")

app.mount("/static", StaticFiles(directory="static"), name="static")

class NovoPreco(BaseModel):
    produto_id: int
    mercado_id: int
    valor: float = Field(gt=0)   # precisa ser maior que zero
    data_coleta: date
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

@app.get("/coleta")
def pagina_coleta():
    return FileResponse("static/coleta.html")


@app.get("/api/mercados")
def mercados():
    return listar_mercados()


@app.get("/api/produtos")
def produtos():
    return listar_produtos()


@app.post("/api/precos", status_code=201)
def cadastrar_preco(preco: NovoPreco):
    try:
        inserir_preco(
            preco.produto_id,
            preco.mercado_id,
            preco.valor,
            preco.data_coleta.isoformat(),
        )
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))
    return {"mensagem": "Preço cadastrado com sucesso."}


@app.post("/api/importar-csv")
async def importar(arquivo: UploadFile = File(...)):  # noqa: B008
    conteudo = await arquivo.read()
    try:
        return importar_csv(conteudo)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro))