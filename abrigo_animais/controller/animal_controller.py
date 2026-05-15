"""
controller/animal_controller.py
Orquestra Model <-> DAO; aplica validações (REQ-B3, REQ-C4).
"""

from model.animal import Animal
from dao.animal_dao import AnimalDAO
from dao.log_dao import LogDAO
from util.validacao import sanitizar_texto, validar_inteiro_positivo

_animal_dao = AnimalDAO()
_log = LogDAO()


def cadastrar_animal(nome, especie, raca, idade, descricao,
                     usuario_logado: str = "sistema") -> Animal:
    # REQ-C4: sanitização
    nome = sanitizar_texto(nome, 100)
    especie = sanitizar_texto(especie, 50)
    raca = sanitizar_texto(raca, 50)
    descricao = sanitizar_texto(descricao, 500)
    idade = validar_inteiro_positivo(str(idade), "Idade")

    if not nome:
        raise ValueError("Nome do animal é obrigatório.")
    if not especie:
        raise ValueError("Espécie do animal é obrigatória.")

    animal = Animal(nome=nome, especie=especie, raca=raca,
                    idade=idade, descricao=descricao)
    animal.id = _animal_dao.inserir(animal)

    # REQ-C3: auditoria
    _log.registrar("CADASTRO_ANIMAL",
                   usuario=usuario_logado,
                   detalhe=f"Animal id={animal.id} nome={nome}")
    return animal


def listar_animais_disponiveis() -> list:
    return _animal_dao.listar_disponiveis()


def listar_todos_animais() -> list:
    return _animal_dao.listar_todos()


def remover_animal(animal_id: int, usuario_logado: str = "sistema") -> bool:
    animal_id = int(animal_id)
    ok = _animal_dao.remover(animal_id)
    if ok:
        _log.registrar("REMOCAO_ANIMAL",
                       usuario=usuario_logado,
                       detalhe=f"Animal id={animal_id}")
    return ok
