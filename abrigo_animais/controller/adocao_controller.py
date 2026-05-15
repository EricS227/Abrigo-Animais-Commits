"""
controller/adocao_controller.py
REQ-B3: validações internas que impedem spoofing (CWE-290).
        O controller valida o estado do negócio independentemente
        de como foi chamado (via CLI ou import direto).
REQ-A1: confirmação dupla tratada na View; log de auditoria aqui.
"""

import datetime
from model.adocao import Adocao
from dao.adocao_dao import AdocaoDAO
from dao.animal_dao import AnimalDAO
from dao.tutor_dao import TutorDAO
from dao.log_dao import LogDAO

_adocao_dao = AdocaoDAO()
_animal_dao = AnimalDAO()
_tutor_dao = TutorDAO()
_log = LogDAO()


def realizar_adocao(animal_id: int, tutor_id: int,
                    usuario_logado: str = "sistema") -> Adocao:
    """
    REQ-B3: valida existência e estado do animal/tutor ANTES de persistir.
    Raise ValueError para qualquer condição inválida.
    """
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
