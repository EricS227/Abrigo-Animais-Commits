"""
view/cli.py
View MVC — Interface CLI.
Telas: T1 (menu inicial), T2 (cadastro), T3 (login), T4 (CRUD animais/tutores/adoções)
REQ-A1: confirmação dupla (S/N) nas operações críticas
"""

import getpass
import os

import controller.auth_controller as auth_ctrl
import controller.animal_controller as animal_ctrl
import controller.tutor_controller as tutor_ctrl
import controller.adocao_controller as adocao_ctrl
from dao.log_dao import LogDAO

_log = LogDAO()
_usuario_logado = None   # guarda username após login


# ──────────────────────────────────────────────
#  Utilitários de exibição
# ──────────────────────────────────────────────

def _limpar():
    os.system("cls" if os.name == "nt" else "clear")


def _linha(char="─", n=56):
    print(char * n)


def _titulo(txt):
    _linha()
    print(f"  {txt}")
    _linha()


def _pause():
    input("\n  [Enter para continuar]")


def _confirmar(msg="Confirmar? (S/N): ") -> bool:
    return input(msg).strip().upper() == "S"


# ──────────────────────────────────────────────
#  T1 — Tela Inicial
#  Requisitos: REQ-C3 (registro de acesso)
# ──────────────────────────────────────────────

def tela_inicial():
    """T1 — Ponto de entrada do sistema."""
    while True:
        _limpar()
        print("""
  ╔══════════════════════════════════════════════╗
  ║      SISTEMA DE ABRIGO DE ANIMAIS  v1.0      ║
  ║         PUCPR — Software Seguro 2026         ║
  ╚══════════════════════════════════════════════╝

    [1] Entrar (Login)
    [2] Cadastrar novo usuário
    [0] Sair
        """)
        opcao = input("  Opção: ").strip()

        if opcao == "1":
            tela_login()
        elif opcao == "2":
            tela_cadastro_usuario()
        elif opcao == "0":
            print("\n  Até logo!\n")
            break
        else:
            print("  Opção inválida.")
            _pause()


# ──────────────────────────────────────────────
#  T2 — Cadastro de Usuário
#  Requisitos: REQ-C2 (bcrypt), REQ-C4 (validação)
# ──────────────────────────────────────────────

def tela_cadastro_usuario():
    """T2 — Formulário de criação de conta."""
    _limpar()
    _titulo("T2 — CADASTRO DE USUÁRIO")
    print("  Requisitos: REQ-C2 (bcrypt+salt) | REQ-C4 (validação de entrada)\n")

    username = input("  Username (3–30 chars, letras/números/_): ").strip()
    senha = getpass.getpass("  Senha (mín. 8 chars, 1 letra, 1 número): ")
    confirmacao = getpass.getpass("  Confirme a senha: ")

    if senha != confirmacao:
        print("\n  ERRO: As senhas não coincidem.")
        _pause()
        return

    try:
        usuario = auth_ctrl.cadastrar_usuario(username, senha)
        print(f"\n  ✔ Usuário '{usuario.username}' cadastrado com sucesso!")
    except ValueError as e:
        print(f"\n  ERRO: {e}")

    _pause()


# ──────────────────────────────────────────────
#  T3 — Autenticação (Login)
#  Requisitos: REQ-C1 (bloqueio 5 tentativas), REQ-C2 (bcrypt), REQ-C3 (log)
# ──────────────────────────────────────────────

def tela_login():
    """T3 — Login com proteção contra força bruta."""
    global _usuario_logado
    _limpar()
    _titulo("T3 — AUTENTICAÇÃO")
    print("  Requisitos: REQ-C1 (bloqueio) | REQ-C2 (bcrypt) | REQ-C3 (log)\n")

    username = input("  Username: ").strip()
    senha = getpass.getpass("  Senha: ")

    try:
        usuario = auth_ctrl.autenticar(username, senha)
        _usuario_logado = usuario.username
        print(f"\n  ✔ Bem-vindo, {_usuario_logado}!")
        _pause()
        menu_principal()
    except ValueError as e:
        print(f"\n  ERRO: {e}")
        _pause()


# ──────────────────────────────────────────────
#  Menu principal (após login)
# ──────────────────────────────────────────────

def menu_principal():
    while True:
        _limpar()
        print(f"""
  ╔══════════════════════════════════════════════╗
  ║  Logado como: {_usuario_logado:<31}║
  ╚══════════════════════════════════════════════╝

    [1] Gerenciar Animais (T4)
    [2] Gerenciar Tutores
    [3] Realizar / Listar Adoções
    [4] Ver logs de auditoria
    [0] Sair (Logout)
        """)
        opcao = input("  Opção: ").strip()

        if opcao == "1":
            menu_animais()
        elif opcao == "2":
            menu_tutores()
        elif opcao == "3":
            menu_adocoes()
        elif opcao == "4":
            tela_logs()
        elif opcao == "0":
            _log.registrar("LOGOUT", usuario=_usuario_logado)
            break
        else:
            print("  Opção inválida.")
            _pause()


# ──────────────────────────────────────────────
#  T4 — CRUD de Animais (modelo de domínio)
#  Requisitos: REQ-B1 (SQL param), REQ-B3 (validação), REQ-C4
# ──────────────────────────────────────────────

def menu_animais():
    """T4 — CRUD do modelo de domínio principal (Animal)."""
    while True:
        _limpar()
        _titulo("T4 — GERENCIAR ANIMAIS")
        print("  Requisitos: REQ-B1 (SQL param.) | REQ-B3 (validação) | REQ-C4\n")
        print("    [1] Cadastrar animal")
        print("    [2] Listar animais disponíveis")
        print("    [3] Listar todos os animais")
        print("    [4] Remover animal")
        print("    [0] Voltar")
        opcao = input("\n  Opção: ").strip()

        if opcao == "1":
            _cadastrar_animal()
        elif opcao == "2":
            _listar_animais(apenas_disponiveis=True)
        elif opcao == "3":
            _listar_animais(apenas_disponiveis=False)
        elif opcao == "4":
            _remover_animal()
        elif opcao == "0":
            break


def _cadastrar_animal():
    _limpar()
    _titulo("CADASTRAR ANIMAL")
    try:
        nome = input("  Nome: ")
        especie = input("  Espécie (cachorro/gato/outro): ")
        raca = input("  Raça: ")
        idade = input("  Idade (anos): ")
        descricao = input("  Descrição: ")

        animal = animal_ctrl.cadastrar_animal(
            nome, especie, raca, idade, descricao,
            usuario_logado=_usuario_logado
        )
        print(f"\n  ✔ Animal cadastrado: {animal}")
    except ValueError as e:
        print(f"\n  ERRO: {e}")
    _pause()


def _listar_animais(apenas_disponiveis: bool):
    _limpar()
    titulo = "ANIMAIS DISPONÍVEIS" if apenas_disponiveis else "TODOS OS ANIMAIS"
    _titulo(titulo)
    animais = (animal_ctrl.listar_animais_disponiveis()
               if apenas_disponiveis else animal_ctrl.listar_todos_animais())
    if not animais:
        print("  Nenhum animal encontrado.")
    for a in animais:
        print(f"  {a}")
    _pause()


def _remover_animal():
    _limpar()
    _titulo("REMOVER ANIMAL")
    animal_id = input("  ID do animal a remover: ").strip()
    if not _confirmar(f"  Confirma remoção do animal id={animal_id}? (S/N): "):
        print("  Operação cancelada.")
        _pause()
        return
    try:
        ok = animal_ctrl.remover_animal(int(animal_id), usuario_logado=_usuario_logado)
        if ok:
            print("  ✔ Animal removido.")
        else:
            print("  Animal não encontrado.")
    except Exception as e:
        print(f"  ERRO: {e}")
    _pause()


# ──────────────────────────────────────────────
#  Tutores
# ──────────────────────────────────────────────

def menu_tutores():
    while True:
        _limpar()
        _titulo("GERENCIAR TUTORES")
        print("    [1] Cadastrar tutor")
        print("    [2] Listar tutores")
        print("    [0] Voltar")
        opcao = input("\n  Opção: ").strip()
        if opcao == "1":
            _cadastrar_tutor()
        elif opcao == "2":
            _listar_tutores()
        elif opcao == "0":
            break


def _cadastrar_tutor():
    _limpar()
    _titulo("CADASTRAR TUTOR")
    try:
        nome = input("  Nome: ")
        cpf = input("  CPF (somente números): ")
        telefone = input("  Telefone: ")
        email = input("  E-mail: ")
        tutor = tutor_ctrl.cadastrar_tutor(
            nome, cpf, telefone, email, usuario_logado=_usuario_logado
        )
        print(f"\n  ✔ Tutor cadastrado: {tutor}")
    except ValueError as e:
        print(f"\n  ERRO: {e}")
    _pause()


def _listar_tutores():
    _limpar()
    _titulo("LISTA DE TUTORES")
    tutores = tutor_ctrl.listar_tutores()
    if not tutores:
        print("  Nenhum tutor cadastrado.")
    for t in tutores:
        print(f"  {t}")
    _pause()


# ──────────────────────────────────────────────
#  Adoções
#  REQ-A1: confirmação dupla (S/N) antes de persistir
# ──────────────────────────────────────────────

def menu_adocoes():
    while True:
        _limpar()
        _titulo("ADOÇÕES")
        print("    [1] Realizar adoção")
        print("    [2] Listar adoções")
        print("    [0] Voltar")
        opcao = input("\n  Opção: ").strip()
        if opcao == "1":
            _realizar_adocao()
        elif opcao == "2":
            _listar_adocoes()
        elif opcao == "0":
            break


def _realizar_adocao():
    _limpar()
    _titulo("REALIZAR ADOÇÃO")
    print("  Requisitos: REQ-A1 (confirmação dupla) | REQ-B3 (validação controller)\n")

    # Exibe listas para auxiliar
    print("  -- Animais disponíveis --")
    for a in animal_ctrl.listar_animais_disponiveis():
        print(f"     {a}")
    print()

    try:
        animal_id = input("  ID do animal: ").strip()
        tutor_id = input("  ID do tutor: ").strip()

        # REQ-A1: confirmação dupla
        print(f"\n  Você deseja adotar o animal id={animal_id} "
              f"para o tutor id={tutor_id}?")
        if not _confirmar("  Confirma a adoção? (S/N): "):
            print("  Operação cancelada.")
            _pause()
            return

        adocao = adocao_ctrl.realizar_adocao(
            int(animal_id), int(tutor_id), usuario_logado=_usuario_logado
        )
        print(f"\n  ✔ Adoção registrada: {adocao}")
    except ValueError as e:
        print(f"\n  ERRO: {e}")
    _pause()


def _listar_adocoes():
    _limpar()
    _titulo("ADOÇÕES REALIZADAS")
    adocoes = adocao_ctrl.listar_adocoes()
    if not adocoes:
        print("  Nenhuma adoção registrada.")
    for a in adocoes:
        print(f"  {a}")
    _pause()


# ──────────────────────────────────────────────
#  Logs de auditoria (REQ-C3)
# ──────────────────────────────────────────────

def tela_logs():
    _limpar()
    _titulo("LOGS DE AUDITORIA (últimos 50)")
    logs = _log.listar()
    if not logs:
        print("  Nenhum registro.")
    for l in logs:
        print(f"  [{l['timestamp']}] {l['usuario'] or '-':15} | "
              f"{l['acao']:25} | {l['detalhe'] or ''}")
    _pause()
