"""
controller/auth_controller.py
REQ-C1: bloqueio após 5 tentativas inválidas (CWE-307)
REQ-C2: bcrypt com salt para armazenamento de senha (CWE-916)
REQ-C3: log de auditoria para login/logout/cadastro
REQ-A3: login OK abre a sessão usada para liberar operações sensíveis.
"""

import datetime
import bcrypt

from model.usuario import Usuario
from dao.usuario_dao import UsuarioDAO
from dao.log_dao import LogDAO
from util.validacao import validar_username, validar_senha
from util.sessao import iniciar_sessao

_usuario_dao = UsuarioDAO()
_log = LogDAO()

MAX_TENTATIVAS = 5
TEMPO_BLOQUEIO_MINUTOS = 15


def cadastrar_usuario(username: str, senha: str) -> Usuario:
    # REQ-C4: valida formato
    username = validar_username(username)
    senha = validar_senha(senha)

    if _usuario_dao.buscar_por_username(username):
        raise ValueError("Username já em uso.")

    # REQ-C2: bcrypt com salt automático
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    usuario = Usuario(username=username, senha_hash=senha_hash)
    usuario.id = _usuario_dao.inserir(usuario)

    _log.registrar("CADASTRO_USUARIO", usuario=username,
                   detalhe="Novo usuário cadastrado")
    return usuario


def autenticar(username: str, senha: str) -> Usuario:
    """
    REQ-C1: verifica bloqueio; incrementa tentativas; bloqueia após 5 falhas.
    REQ-C2: compara senha com bcrypt.
    Retorna Usuario se autenticado, raise ValueError caso contrário.
    """
    username = username.strip()
    usuario = _usuario_dao.buscar_por_username(username)

    # Usuário não existe — mensagem genérica (REQ-A1 / STRIDE I)
    if not usuario:
        _log.registrar("LOGIN_FALHA", usuario=username,
                       detalhe="Usuário não encontrado")
        raise ValueError("Usuário ou senha inválidos.")

    # REQ-C1: verifica bloqueio ativo
    if usuario.bloqueado_ate:
        bloqueado_ate = datetime.datetime.fromisoformat(usuario.bloqueado_ate)
        if datetime.datetime.now() < bloqueado_ate:
            restante = int((bloqueado_ate - datetime.datetime.now()).total_seconds() / 60) + 1
            raise ValueError(
                f"Conta bloqueada. Tente novamente em {restante} minuto(s)."
            )
        else:
            # Desbloqueio automático após expirar o tempo
            _usuario_dao.resetar_tentativas(username)
            usuario.tentativas_falhas = 0
            usuario.bloqueado_ate = None

    # REQ-C2: verificação bcrypt
    senha_correta = bcrypt.checkpw(senha.encode(), usuario.senha_hash.encode())

    if not senha_correta:
        novas_tentativas = usuario.tentativas_falhas + 1
        bloqueado_ate = None

        if novas_tentativas >= MAX_TENTATIVAS:
            bloqueado_ate = (
                datetime.datetime.now() +
                datetime.timedelta(minutes=TEMPO_BLOQUEIO_MINUTOS)
            ).isoformat()
            _usuario_dao.atualizar_tentativas(username, novas_tentativas, bloqueado_ate)
            _log.registrar("CONTA_BLOQUEADA", usuario=username,
                           detalhe=f"Bloqueada até {bloqueado_ate}")
            raise ValueError(
                f"Conta bloqueada por {TEMPO_BLOQUEIO_MINUTOS} minutos "
                f"após {MAX_TENTATIVAS} tentativas inválidas."
            )

        _usuario_dao.atualizar_tentativas(username, novas_tentativas)
        _log.registrar("LOGIN_FALHA", usuario=username,
                       detalhe=f"Tentativa {novas_tentativas}/{MAX_TENTATIVAS}")
        raise ValueError(
            f"Usuário ou senha inválidos. "
            f"Tentativa {novas_tentativas}/{MAX_TENTATIVAS}."
        )

    # Login bem-sucedido
    _usuario_dao.resetar_tentativas(username)
    iniciar_sessao(username)   # REQ-A3
    _log.registrar("LOGIN_SUCESSO", usuario=username)
    return usuario
