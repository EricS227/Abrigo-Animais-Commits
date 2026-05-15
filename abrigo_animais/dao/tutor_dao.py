"""
dao/tutor_dao.py
Padrão: Repository
REQ-B1: prepared statements em todas as queries
"""

from dao.database import get_connection
from model.tutor import Tutor


class TutorDAO:

    def inserir(self, tutor: Tutor) -> int:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO tutor (nome, cpf, telefone, email) VALUES (?, ?, ?, ?)",
            (tutor.nome, tutor.cpf, tutor.telefone, tutor.email)
        )
        conn.commit()
        return cur.lastrowid

    def listar(self) -> list[Tutor]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM tutor").fetchall()
        return [Tutor(**dict(r)) for r in rows]

    def buscar_por_id(self, tutor_id: int):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM tutor WHERE id = ?", (tutor_id,)
        ).fetchone()
        return Tutor(**dict(row)) if row else None

    def buscar_por_cpf(self, cpf: str):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM tutor WHERE cpf = ?", (cpf,)
        ).fetchone()
        return Tutor(**dict(row)) if row else None
