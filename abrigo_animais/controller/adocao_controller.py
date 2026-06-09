"""
controller/adocao_controller.py
REQ-A3 (CWE-290): adoção exige sessão autenticada (ver util/sessao.py);
        chamada direta sem sessão é barrada antes de gravar.
REQ-B3: valida existência e estado do animal/tutor independentemente de quem chama.
REQ-A1: confirmação dupla fica na View; log de auditoria aqui.
"""

import datetime
from model.adocao import Adocao
from dao.adocao_dao import AdocaoDAO
from dao.animal_dao import AnimalDAO
from dao.tutor_dao import TutorDAO
from dao.log_dao import LogDAO
from util.sessao import validar_sessao

_adocao_dao = AdocaoDAO()
_animal_dao = AnimalDAO()
_tutor_dao = TutorDAO()
_log = LogDAO()


def realizar_adocao(animal_id: int, tutor_id: int, sessao=None) -> Adocao:
    """
    REQ-A3: exige sessão autenticada. REQ-B3: valida animal/tutor antes de gravar.
    Levanta PermissionError (origem) ou ValueError (regra de negócio).
    """
    # REQ-A3: sem sessão válida nem chega a olhar os dados
    if not validar_sessao(sessao):
        _log.registrar(
            "ADOCAO_NEGADA",
            usuario=getattr(sessao, "username", None),
            detalhe="Origem não autorizada: sessão inválida ou ausente."
        )
        raise PermissionError(
            "Origem não autorizada: é preciso estar logado para adotar."
        )
    usuario_logado = sessao.username

    # --- Validação de tipos (REQ-C4) ---
    try:
        animal_id = int(animal_id)
        tutor_id = int(tutor_id)
    except (TypeError, ValueError):
        raise ValueError("IDs de animal e tutor devem ser inteiros.")

    # --- REQ-B3: verifica existência ---
    animal = _animal_dao.buscar_por_id(animal_id)
    if not animal:
        raise ValueError(f"Animal id={animal_id} não encontrado.")

    tutor = _tutor_dao.buscar_por_id(tutor_id)
    if not tutor:
        raise ValueError(f"Tutor id={tutor_id} não encontrado.")

    # --- REQ-B3: regra de negócio crítica ---
    if animal.adotado:
        raise ValueError(f"Animal '{animal.nome}' já foi adotado.")

    # --- Persiste ---
    data = datetime.date.today().isoformat()
    adocao = Adocao(animal_id=animal_id, tutor_id=tutor_id, data=data)
    adocao.id = _adocao_dao.inserir(adocao)

    _animal_dao.marcar_adotado(animal_id)

    # REQ-C3: log de auditoria
    _log.registrar(
        "ADOCAO_REALIZADA",
        usuario=usuario_logado,
        detalhe=(f"adocao_id={adocao.id} animal={animal.nome}(id={animal_id}) "
                 f"tutor={tutor.nome}(id={tutor_id})")
    )
    adocao.animal_nome = animal.nome
    adocao.tutor_nome = tutor.nome
    return adocao


def listar_adocoes() -> list:
    return _adocao_dao.listar()
