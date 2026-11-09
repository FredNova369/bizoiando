import csv
import io
import sqlite3
from datetime import datetime

from app.database import get_connection


def buscar_precos(texto: str):
    sql = """
    SELECT
        p.id          AS produto_id,
        p.nome        AS produto,
        p.unidade     AS unidade,
        m.nome        AS mercado,
        m.bairro      AS bairro,
        pr.valor      AS valor,
        pr.data_coleta AS data_coleta
    FROM preco pr
    JOIN produto p ON p.id = pr.produto_id
    JOIN mercado m ON m.id = pr.mercado_id
    WHERE p.nome LIKE ?
      AND pr.id = (
            SELECT id FROM preco
            WHERE produto_id = pr.produto_id
              AND mercado_id = pr.mercado_id
            ORDER BY data_coleta DESC, id DESC
            LIMIT 1
      )
    ORDER BY p.nome, pr.valor ASC
    """
    with get_connection() as conn:
        linhas = conn.execute(sql, (f"%{texto}%",)).fetchall()

    
    produtos = {}
    for linha in linhas:
        pid = linha["produto_id"]
        if pid not in produtos:
            produtos[pid] = {
                "produto": linha["produto"],
                "unidade": linha["unidade"],
                "precos": [],
            }
        produtos[pid]["precos"].append({
            "mercado": linha["mercado"],
            "bairro": linha["bairro"],
            "valor": linha["valor"],
            "data_coleta": linha["data_coleta"],
        })

    resultados = []
    for item in produtos.values():
        item["mais_barato"] = item["precos"][0]
        resultados.append(item)
    return resultados

def listar_mercados():
    with get_connection() as conn:
        linhas = conn.execute("SELECT id, nome, bairro FROM mercado ORDER BY nome")
        return [dict(l) for l in linhas]


def listar_produtos():
    with get_connection() as conn:
        linhas = conn.execute("SELECT id, nome, unidade FROM produto ORDER BY nome")
        return [dict(l) for l in linhas]


def inserir_preco(produto_id: int, mercado_id: int, valor: float, data_coleta: str):
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO preco (produto_id, mercado_id, valor, data_coleta) "
                "VALUES (?, ?, ?, ?)",
                (produto_id, mercado_id, valor, data_coleta),
            )
    except sqlite3.IntegrityError:
        # Acontece quando o produto ou o mercado não existe (chave estrangeira)
        raise ValueError("Produto ou mercado inexistente.")


def _normalizar_data(texto: str) -> str:
    """Aceita 2026-11-16 ou 16/11/2026 e devolve sempre 2026-11-16."""
    texto = texto.strip()
    for formato in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto, formato).date().isoformat()
        except ValueError:
            pass
    raise ValueError("data inválida (use AAAA-MM-DD ou DD/MM/AAAA)")


def importar_csv(conteudo: bytes):
    # O Excel brasileiro costuma salvar em cp1252; tentamos UTF-8 primeiro
    try:
        texto = conteudo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = conteudo.decode("cp1252")

    if not texto.strip():
        raise ValueError("O arquivo está vazio.")

    # O Excel brasileiro usa ";" como separador; outros programas usam ","
    primeira_linha = texto.splitlines()[0]
    separador = ";" if ";" in primeira_linha else ","

    leitor = csv.DictReader(io.StringIO(texto), delimiter=separador)
    leitor.fieldnames = [c.strip().lower() for c in (leitor.fieldnames or [])]

    obrigatorias = {"produto", "mercado", "valor", "data_coleta"}
    if not obrigatorias.issubset(leitor.fieldnames):
        raise ValueError(
            "O cabeçalho precisa ter as colunas: produto, mercado, valor, data_coleta."
        )

    importados = 0
    erros = []

    with get_connection() as conn:
        produtos = {l["nome"].lower(): l["id"] for l in conn.execute("SELECT id, nome FROM produto")}
        mercados = {l["nome"].lower(): l["id"] for l in conn.execute("SELECT id, nome FROM mercado")}

        for numero, linha in enumerate(leitor, start=2):  # linha 1 é o cabeçalho
            try:
                produto_id = produtos.get((linha["produto"] or "").strip().lower())
                if produto_id is None:
                    raise ValueError("produto não cadastrado")

                mercado_id = mercados.get((linha["mercado"] or "").strip().lower())
                if mercado_id is None:
                    raise ValueError("mercado não cadastrado")

                try:
                    valor = float((linha["valor"] or "").strip().replace(",", "."))
                except ValueError:
                    raise ValueError("valor inválido")
                if valor <= 0:
                    raise ValueError("o valor precisa ser maior que zero")

                data_coleta = _normalizar_data(linha["data_coleta"] or "")

                conn.execute(
                    "INSERT INTO preco (produto_id, mercado_id, valor, data_coleta) "
                    "VALUES (?, ?, ?, ?)",
                    (produto_id, mercado_id, valor, data_coleta),
                )
                importados += 1
            except ValueError as erro:
                erros.append({"linha": numero, "motivo": str(erro)})

    return {"importados": importados, "erros": erros}