"""
dao/database.py
Padrões: Singleton (get_connection) + Template Method (init_db)
REQ-A2/B2: dados em repouso — banco cifrado com SQLCipher quando disponível,
           senão sqlite3 + chmod 600. Chave vem do ambiente (ABRIGO_DB_KEY).
"""

import os
import stat

# Usa SQLCipher se estiver instalado; senão volta pro sqlite3 padrão.
try:
    import sqlcipher3.dbapi2 as _driver
    CIFRAGEM_ATIVA = True
except Exception:
    import sqlite3 as _driver
    CIFRAGEM_ATIVA = False

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "abrigo.db")
DB_PATH = os.path.normpath(DB_PATH)

# REQ-A2/B2: chave não fica no código — vem do ambiente. O default é só pra
# facilitar testes; em uso real define-se ABRIGO_DB_KEY.
DB_KEY = os.environ.get("ABRIGO_DB_KEY", "abrigo-dev-key-trocar-em-producao")

_connection = None  # instância única – Singleton


def _aplicar_chave(conn) -> None:
    # PRAGMA key tem que vir antes de qualquer query; não aceita placeholder,
    # então escapamos aspas simples na chave (que vem do ambiente).
    if not CIFRAGEM_ATIVA:
        return
    chave = DB_KEY.replace("'", "''")
    conn.execute(f"PRAGMA key = '{chave}'")


def get_connection():
    """Singleton: retorna sempre a mesma conexão ao banco."""
    global _connection
    if _connection is None:
        _connection = _driver.connect(DB_PATH)
        _aplicar_chave(_connection)
        _connection.row_factory = _driver.Row
        _connection.execute("PRAGMA foreign_keys = ON")
    return _connection


def init_db() -> None:
    """
    Template Method: cria as tabelas e protege o arquivo do banco (REQ-A2/B2).
    """
    conn = get_connection()
    cursor = conn.cursor()

    if CIFRAGEM_ATIVA:
        print("[seguranca] Banco cifrado em repouso (SQLCipher/AES-256).")
        if DB_KEY == "abrigo-dev-key-trocar-em-producao":
            print("[seguranca] Aviso: chave padrao de dev. Defina ABRIGO_DB_KEY.")
    else:
        print("[seguranca] Sem SQLCipher: usando sqlite3 + chmod 600.")

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
