"""model/tutor.py — Entidade Tutor"""


class Tutor:
    def __init__(self, id=None, nome="", cpf="", telefone="", email=""):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.telefone = telefone
        self.email = email

    def __repr__(self):
        return f"[{self.id}] {self.nome} | CPF: {self.cpf} | Tel: {self.telefone}"
