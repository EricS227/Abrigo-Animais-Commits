"""
main.py — Ponto de entrada do sistema.
Inicializa o banco de dados e chama a View (CLI).
"""

from dao.database import init_db
from view.cli import tela_inicial


def main():
    init_db()          # cria tabelas + chmod 600 (REQ-B2)
    tela_inicial()     # T1 — Tela Inicial


if __name__ == "__main__":
    main()
