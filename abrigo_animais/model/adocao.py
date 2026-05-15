"""model/adocao.py — Entidade Adocao"""


class Adocao:
    def __init__(self, id=None, animal_id=None, tutor_id=None, data="",
                 animal_nome="", tutor_nome=""):
        self.id = id
        self.animal_id = animal_id
        self.tutor_id = tutor_id
        self.data = data
        self.animal_nome = animal_nome
        self.tutor_nome = tutor_nome

    def __repr__(self):
        return (f"[{self.id}] Animal: {self.animal_nome} (id={self.animal_id}) | "
                f"Tutor: {self.tutor_nome} (id={self.tutor_id}) | Data: {self.data}")
