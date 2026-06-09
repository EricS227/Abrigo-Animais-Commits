# Sistema de Abrigo de Animais

Trabalho da disciplina Software Seguro — PUCPR 2026, Equipe 11.

Sistema CLI de gerenciamento de abrigo de animais com foco em segurança: prepared statements, bcrypt, bloqueio de login e log de auditoria.

---

## Pré-requisitos

- Python 3.10 ou superior
- bcrypt 4.0.0 ou superior

---

## Instalação

```bash
git clone https://github.com/EricS227/Roku-Shichi-Sechs-Sieben.git
cd Abrigo-Animais-Commits/abrigo_animais
pip install -r requirements.txt
python main.py
```

---

## Telas

**T1 — Menu inicial:** opções de login, cadastro de usuário e saída.

**T2 — Cadastro de usuário:** define username e senha. A senha é armazenada como hash bcrypt, nunca em texto puro.

**T3 — Login:** autentica o operador. Após 5 tentativas inválidas a conta é bloqueada por 15 minutos.

**T4 — Gerenciar animais:** cadastrar, listar disponíveis, listar todos e remover. Operações críticas pedem confirmação antes de executar.

Após o login também é possível gerenciar tutores, registrar adoções e consultar o log de auditoria.

---

## Testes

```bash
# Executar a partir de abrigo_animais/
python -m pytest tests/test_sql_injection.py -v
```

Cobre prevenção contra SQL Injection nos métodos `inserir()` e `listar_disponiveis()` do `AnimalDAO`.
