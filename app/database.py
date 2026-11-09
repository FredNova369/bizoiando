import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).resolve().parent.parent / "bizoiando.db"


def get_connection():
    conn = sqlite3.connect(CAMINHO_BANCO)
    conn.row_factory = sqlite3.Row          # permite acessar colunas pelo nome
    conn.execute("PRAGMA foreign_keys = ON")  # ativa a checagem das chaves estrangeiras
    return conn


def criar_tabelas():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS mercado (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            nome   TEXT NOT NULL UNIQUE,
            bairro TEXT
        );

        CREATE TABLE IF NOT EXISTS produto (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT NOT NULL UNIQUE,
            categoria TEXT,
            unidade   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS preco (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id  INTEGER NOT NULL,
            mercado_id  INTEGER NOT NULL,
            valor       REAL NOT NULL,
            data_coleta TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produto(id),
            FOREIGN KEY (mercado_id) REFERENCES mercado(id)
        );
        """)