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