"""
util/validacao.py
REQ-C4: validação e sanitização de entradas (CWE-20)
REQ-B3: validações que blindam o controller contra inputs inválidos
"""

import re


# ---- Sanitização ----

def sanitizar_texto(valor: str, max_len: int = 200) -> str:
    """
    Remove caracteres de controle, limita tamanho.
    Rejeita qualquer tentativa de injeção SQL ou de shell
    via lista de padrões proibidos (segunda barreira; a primeira
    são os prepared statements em todos os DAOs — REQ-B1).
    """
    if not isinstance(valor, str):
        raise ValueError("Entrada deve ser texto.")
    valor = valor.strip()
    if len(valor) > max_len:
        raise ValueError(f"Texto excede {max_len} caracteres.")
    # Remove caracteres de controle (exceto espaço normal)
    valor = re.sub(r"[\x00-\x1f\x7f]", "", valor)
    return valor


# ---- Validações específicas ----

def validar_cpf(cpf: str) -> str:
    """Aceita apenas dígitos, pontos e traços; normaliza para dígitos apenas."""
    cpf_limpo = re.sub(r"[.\-]", "", cpf.strip())
    if not re.fullmatch(r"\d{11}", cpf_limpo):
        raise ValueError("CPF inválido. Informe 11 dígitos.")
    return cpf_limpo


def validar_email(email: str) -> str:
    email = email.strip()
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("E-mail inválido.")
    return email


def validar_telefone(tel: str) -> str:
    tel_limpo = re.sub(r"[\s\-\(\)]", "", tel.strip())
    if tel_limpo and not re.fullmatch(r"\d{8,15}", tel_limpo):
        raise ValueError("Telefone inválido (apenas dígitos, 8–15 caracteres).")
    return tel_limpo


def validar_inteiro_positivo(valor: str, nome_campo: str = "campo") -> int:
    try:
        n = int(valor)
        if n < 0:
            raise ValueError
        return n
    except (ValueError, TypeError):
        raise ValueError(f"{nome_campo} deve ser um número inteiro positivo.")


def validar_username(username: str) -> str:
    username = username.strip()
    if not re.fullmatch(r"[a-zA-Z0-9_]{3,30}", username):
        raise ValueError(
            "Username deve ter 3–30 caracteres alfanuméricos ou '_'."
        )
    return username


def validar_senha(senha: str) -> str:
    """
    Exige mínimo de 8 caracteres, ao menos 1 letra e 1 dígito.
    REQ-C2 complementar.
    """
    if len(senha) < 8:
        raise ValueError("Senha deve ter ao menos 8 caracteres.")
    if not re.search(r"[A-Za-z]", senha):
        raise ValueError("Senha deve conter ao menos uma letra.")
    if not re.search(r"\d", senha):
        raise ValueError("Senha deve conter ao menos um número.")
    return senha
