"""
controller/tutor_controller.py
Orquestra Model <-> DAO; aplica validações (REQ-B3, REQ-C4).
"""

from model.tutor import Tutor
from dao.tutor_dao import TutorDAO
from dao.log_dao import LogDAO
from util.validacao import sanitizar_texto, validar_cpf, validar_email, validar_telefone

_tutor_dao = TutorDAO()
_log = LogDAO()


def cadastrar_tutor(nome, cpf, telefone, email,
                    usuario_logado: str = "sistema") -> Tutor:
    # REQ-C4: sanitização e validação
    nome = sanitizar_texto(nome, 100)
    cpf = validar_cpf(cpf)
    telefone = validar_telefone(telefone)
    email = validar_email(email)

    if not nome:
        raise ValueError("Nome do tutor é obrigatório.")

    # Verifica duplicidade de CPF
    if _tutor_dao.buscar_por_cpf(cpf):
        raise ValueError("CPF já cadastrado no sistema.")

    tutor = Tutor(nome=nome, cpf=cpf, telefone=telefone, email=email)
    tutor.id = _tutor_dao.inserir(tutor)

    _log.registrar("CADASTRO_TUTOR",
                   usuario=usuario_logado,
                   detalhe=f"Tutor id={tutor.id} cpf={cpf[:3]}***")
    return tutor


def listar_tutores() -> list:
    return _tutor_dao.listar()
