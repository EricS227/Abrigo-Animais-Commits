"""model/animal.py — Entidade Animal"""


class Animal:
    def __init__(self, id=None, nome="", especie="", raca="",
                 idade=0, descricao="", adotado=0):
        self.id = id
        self.nome = nome
        self.especie = especie
        self.raca = raca
        self.idade = idade
        self.descricao = descricao
        self.adotado = bool(adotado)

    def __repr__(self):
        status = "Adotado" if self.adotado else "Disponivel"
        return (f"[{self.id}] {self.nome} | {self.especie} | {self.raca} | "
                f"{self.idade} anos | {status}")
