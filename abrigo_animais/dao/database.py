"""
dao/database.py
Padrões: Singleton (get_connection) + Template Method (init_db)
Requisito B2: permissão 600 aplicada ao arquivo do banco após criação.
"""

import sqlite3
import os
import stat

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "abrigo.db")
DB_PATH = os.path.normpath(DB_PATH)

_connection = None  # instância única – Singleton


def get_connection() -> sqlite3.Connection:
    """Singleton: retorna sempre a mesma conexão ao banco."""
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(DB_PATH)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON")
    return _connection


def init_db() -> None:
    """
    Template Method: define o algoritmo de inicialização do banco.
    Cria tabelas e aplica chmod 600 (REQ-B2).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de usuários do sistema (operadores do abrigo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT    NOT NULL UNIQUE,
            senha_hash TEXT   NOT NULL,
            tentativas_falhas INTEGER DEFAULT 0,
            bloqueado_ate     TEXT    DEFAULT NULL
        )
    """)

    # Tabela de animais
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS animal (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT    NOT NULL,
            especie   TEXT    NOT NULL,
            raca      TEXT,
            idade     INTEGER,
            descricao TEXT,
            adotado   INTEGER DEFAULT 0
        )
    """)

    # Tabela de tutores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tutor (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT    NOT NULL,
            cpf       TEXT    NOT NULL UNIQUE,
            telefone  TEXT,
            email     TEXT
        )
    """)

    # Tabela de adoções
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS adocao (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id INTEGER NOT NULL,
            tutor_id  INTEGER NOT NULL,
            data      TEXT    NOT NULL,
            FOREIGN KEY (animal_id) REFERENCES animal(id),
            FOREIGN KEY (tutor_id)  REFERENCES tutor(id)
        )
    """)

    # Tabela de logs de auditoria (REQ-C3)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_auditoria (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            usuario   TEXT,
            acao      TEXT    NOT NULL,
            detalhe   TEXT
        )
    """)

    conn.commit()

    # REQ-B2: chmod 600 – somente dono lê/escreve
    if os.path.exists(DB_PATH):
        os.chmod(DB_PATH, stat.S_IRUSR | stat.S_IWUSR)
