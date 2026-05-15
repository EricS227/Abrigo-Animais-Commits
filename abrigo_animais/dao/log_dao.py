"""
dao/log_dao.py
REQ-C3: log de auditoria para ações críticas
"""

import datetime
from dao.database import get_connection


class LogDAO:

    def registrar(self, acao: str, usuario: str = None, detalhe: str = None) -> None:
        conn = get_connection()
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        conn.execute(
            "INSERT INTO log_auditoria (timestamp, usuario, acao, detalhe) "
            "VALUES (?, ?, ?, ?)",
            (ts, usuario, acao, detalhe)
        )
        conn.commit()

    def listar(self) -> list:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM log_auditoria ORDER BY id DESC LIMIT 50"
        ).fetchall()
        return [dict(r) for r in rows]
