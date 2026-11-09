from datetime import date

from app.database import criar_tabelas, get_connection

MERCADOS = [
    ("Vitória Supermercado",   "Centro"),
    ("Hiper DB Nova Cidade",   "Nova Cidade"),
    ("Pátio Gourmet",          "Adrianópolis"),
    ("Carrefour Hipermercado", "Ponta Negra"),
    ("Nova Era Max Teixeira",  "Max Teixeira"),
]

# (nome, categoria, unidade, [preço no Mercado A, B, C, D, E])
PRODUTOS = [
    ("Tomate",           "Legumes",    "kg",      [7.90, 6.99, 8.49, 8.90, 7.49]),
    ("Banana prata",     "Frutas",     "kg",      [6.50, 5.99, 6.89, 7.20, 6.10]),
    ("Alface",           "Verduras",   "unidade", [3.49, 2.99, 3.99, 4.20, 3.29]),
    ("Ovos",             "Ovos",       "dúzia",   [12.90, 11.50, 13.40, 14.00, 12.20]),
    ("Frango inteiro",   "Carnes",     "kg",      [14.90, 13.99, 15.50, 16.20, 14.50]),
    ("Leite integral",   "Laticínios", "litro",   [5.49, 4.99, 5.79, 6.10, 5.29]),
    ("Queijo mussarela", "Laticínios", "kg",      [42.90, 39.90, 44.50, 46.00, 41.50]),
    ("Cenoura",          "Legumes",    "kg",      [5.99, 4.89, 6.20, 6.50, 5.40]),
]


def popular():
    criar_tabelas()
    hoje = date.today().isoformat()

    with get_connection() as conn:
        # Limpa tudo antes (preco primeiro, por causa das chaves estrangeiras)
        conn.execute("DELETE FROM preco")
        conn.execute("DELETE FROM produto")
        conn.execute("DELETE FROM mercado")

        ids_mercados = []
        for nome, bairro in MERCADOS:
            cur = conn.execute(
                "INSERT INTO mercado (nome, bairro) VALUES (?, ?)", (nome, bairro)
            )
            ids_mercados.append(cur.lastrowid)

        for nome, categoria, unidade, precos in PRODUTOS:
            cur = conn.execute(
                "INSERT INTO produto (nome, categoria, unidade) VALUES (?, ?, ?)",
                (nome, categoria, unidade),
            )
            produto_id = cur.lastrowid
            for mercado_id, valor in zip(ids_mercados, precos):
                conn.execute(
                    "INSERT INTO preco (produto_id, mercado_id, valor, data_coleta) "
                    "VALUES (?, ?, ?, ?)",
                    (produto_id, mercado_id, valor, hoje),
                )

    print("Banco populado com dados fictícios.")


if __name__ == "__main__":
    popular()