"""
dao/usuario_dao.py
REQ-C1: controle de tentativas de login (bloqueio após 5 falhas)
REQ-C2: senhas armazenadas com bcrypt (hash + salt)
"""

from dao.database import get_connection
from model.usuario import Usuario


class UsuarioDAO:

    def inserir(self, usuario: Usuario) -> int:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO usuario (username, senha_hash) VALUES (?, ?)",
            (usuario.username, usuario.senha_hash)
        )
        conn.commit()
        return cur.lastrowid

    def buscar_por_username(self, username: str):
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM usuario WHERE username = ?", (username,)
        ).fetchone()
        if not row:
            return None
        return Usuario(**dict(row))

    def atualizar_tentativas(self, username: str, tentativas: int,
                              bloqueado_ate=None) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE usuario SET tentativas_falhas = ?, bloqueado_ate = ? "
            "WHERE username = ?",
            (tentativas, bloqueado_ate, username)
        )
        conn.commit()

    def resetar_tentativas(self, username: str) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE usuario SET tentativas_falhas = 0, bloqueado_ate = NULL "
            "WHERE username = ?",
            (username,)
        )
        conn.commit()
