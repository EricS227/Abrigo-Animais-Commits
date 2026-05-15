"""
dao/animal_dao.py
Padrão: Repository
REQ-B1: todas as queries usam prepared statements (parâmetros ?)
REQ-C4: validação e sanitização de entradas no controller
"""

from dao.database import get_connection
from model.animal import Animal


class AnimalDAO:
    # ------------------------------------------------------------------ #
    #  REQ-B1: TODOS os execute() usam parâmetros ?, nunca f-string/concat
    # ------------------------------------------------------------------ #

    def inserir(self, animal: Animal) -> int:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO animal (nome, especie, raca, idade, descricao, adotado) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (animal.nome, animal.especie, animal.raca,
             animal.idade, animal.descricao, int(animal.adotado))
        )
        conn.commit()
        return cur.lastrowid

    def listar_disponiveis(self) -> list[Animal]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM animal WHERE adotado = 0"
        ).fetchall()
        return [Animal(**dict(r)) for r in rows]

    def listar_todos(self) -> list[Animal]:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM animal").fetchall()
        return [Animal(**dict(r)) for r in rows]

    def buscar_por_id(self, animal_id: int):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM animal WHERE id = ?", (animal_id,)
        ).fetchone()
        return Animal(**dict(row)) if row else None

    def marcar_adotado(self, animal_id: int) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE animal SET adotado = 1 WHERE id = ?", (animal_id,)
        )
        conn.commit()

    def remover(self, animal_id: int) -> bool:
        conn = get_connection()
        cur = conn.execute(
            "DELETE FROM animal WHERE id = ?", (animal_id,)
        )
        conn.commit()
        return cur.rowcount > 0
