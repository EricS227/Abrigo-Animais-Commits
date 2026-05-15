"""
dao/adocao_dao.py
Padrão: Repository
REQ-B1: prepared statements em todas as queries
"""

from dao.database import get_connection
from model.adocao import Adocao


class AdocaoDAO:

    def inserir(self, adocao: Adocao) -> int:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO adocao (animal_id, tutor_id, data) VALUES (?, ?, ?)",
            (adocao.animal_id, adocao.tutor_id, adocao.data)
        )
        conn.commit()
        return cur.lastrowid

    def listar(self) -> list[Adocao]:
        conn = get_connection()
        rows = conn.execute("""
            SELECT a.id, a.animal_id, a.tutor_id, a.data,
                   an.nome AS animal_nome, t.nome AS tutor_nome
            FROM adocao a
            JOIN animal an ON an.id = a.animal_id
            JOIN tutor  t  ON t.id  = a.tutor_id
        """).fetchall()
        return [Adocao(**dict(r)) for r in rows]
