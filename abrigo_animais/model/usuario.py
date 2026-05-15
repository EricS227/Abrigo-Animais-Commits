"""model/usuario.py — Entidade Usuario"""


class Usuario:
    def __init__(self, id=None, username="", senha_hash="",
                 tentativas_falhas=0, bloqueado_ate=None):
        self.id = id
        self.username = username
        self.senha_hash = senha_hash
        self.tentativas_falhas = tentativas_falhas
        self.bloqueado_ate = bloqueado_ate
