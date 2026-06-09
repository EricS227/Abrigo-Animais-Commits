"""
util/sessao.py
REQ-A3 / REQ-B3 (CWE-290): sessão criada só no login autenticado.
Operações sensíveis (adoção) exigem essa sessão; import direto sem ela é barrado.
"""

import secrets
import datetime


class Sessao:
    def __init__(self, username: str):
        self.username = username
        self.token = secrets.token_hex(16)   # segredo não-forjável
        self.criado_em = datetime.datetime.now()


_sessao_ativa = None   # vive só em memória, durante a execução


def iniciar_sessao(username: str) -> Sessao:
    global _sessao_ativa
    _sessao_ativa = Sessao(username)
    return _sessao_ativa


def encerrar_sessao() -> None:
    global _sessao_ativa
    _sessao_ativa = None


def obter_sessao_ativa():
    return _sessao_ativa


def validar_sessao(sessao) -> bool:
    # confere se o objeto recebido é mesmo a sessão ativa (token bate)
    return (
        isinstance(sessao, Sessao)
        and _sessao_ativa is not None
        and secrets.compare_digest(sessao.token, _sessao_ativa.token)
    )
