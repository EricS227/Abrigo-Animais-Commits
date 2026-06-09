# Sistema de Abrigo de Animais

Trabalho da disciplina Software Seguro — PUCPR 2026, Equipe 11.

Sistema CLI de gerenciamento de abrigo de animais com foco em segurança: prepared statements, bcrypt, bloqueio de login e log de auditoria.

---

## Pré-requisitos

- Python 3.10 ou superior
- bcrypt 4.0.0 ou superior
- sqlcipher3 0.6.0 ou superior *(opcional — criptografia em repouso; ver A2/B2)*

---

## Instalação

```bash
git clone https://github.com/EricS227/Roku-Shichi-Sechs-Sieben.git
cd Roku-Shichi-Sechs-Sieben/abrigo_animais
pip install -r requirements.txt

# (opcional) define a chave de criptografia do banco em repouso.
# Sem definir, é usada uma chave de desenvolvimento (o sistema avisa).
#   Windows PowerShell:  $env:ABRIGO_DB_KEY = "uma-chave-forte"
#   Linux/macOS:         export ABRIGO_DB_KEY="uma-chave-forte"

python main.py
```

> Se a instalação do `sqlcipher3` falhar no seu ambiente (precisa da lib
> nativa SQLCipher), remova essa linha do `requirements.txt`: o sistema
> roda normalmente caindo para `sqlite3` + `chmod 600` (ver A2/B2 abaixo).

---

## Telas

**T1 — Menu inicial:** opções de login, cadastro de usuário e saída.

**T2 — Cadastro de usuário:** define username e senha. A senha é armazenada como hash bcrypt, nunca em texto puro.

**T3 — Login:** autentica o operador. Após 5 tentativas inválidas a conta é bloqueada por 15 minutos.

**T4 — Gerenciar animais:** cadastrar, listar disponíveis, listar todos e remover. Operações críticas pedem confirmação antes de executar.

Após o login também é possível gerenciar tutores, registrar adoções e consultar o log de auditoria.

---

## Arquitetura e Design Patterns

MVC + camada DAO:

| Padrão | Onde |
|--------|------|
| **MVC** | `model/` (entidades), `view/cli.py` (telas), `controller/` (regras de orquestração) |
| **DAO** | `dao/*_dao.py` — todo acesso a dados isolado dos controllers |
| **Singleton** | `dao/database.py::get_connection()` (conexão única) e a sessão única em memória (`util/sessao.py`) |
| **Template Method** | `dao/database.py::init_db()` encapsula o algoritmo de criação do schema |
| **Repository** | os DAOs expõem coleções de entidades (`listar`, `buscar_por_id`, etc.) |

---

## Requisitos de segurança — comportamento **real** no código

| Req | CWE | Onde está verificável | O que faz |
|-----|-----|-----------------------|-----------|
| **A1** Tampering/IDs | CWE-639 | `controller/adocao_controller.py` | valida IDs e estado antes de gravar |
| **A2** Info disclosure (banco) | CWE-312 | `dao/database.py` | **banco cifrado com SQLCipher** quando disponível; fallback chmod 600 |
| **A3** Spoofing de origem | CWE-290 | `util/sessao.py` + `adocao_controller.py` | adoção exige **sessão autenticada**; import direto é barrado |
| **B1** SQL Injection | CWE-89 | todos os `dao/*_dao.py` | prepared statements (`?`) em 100% das queries |
| **B2** Dados em repouso | CWE-312 | `dao/database.py` | SQLCipher (AES-256) + `chmod 600` + `.gitignore` |
| **B3** Anti-spoofing no controller | CWE-290 | `adocao_controller.py` | valida origem **e** regra de negócio independentemente de quem chamou |
| **C1** Bloqueio de conta | CWE-307 | `auth_controller.py` | bloqueio 15 min após 5 falhas; persistido em `usuario` |
| **C2** Hash de senha | CWE-916 | `auth_controller.py` | bcrypt + salt (`hashpw`/`checkpw`) |
| **C3** Log de auditoria | CWE-778 | `dao/log_dao.py` | login OK/falho, cadastro, adoção, adoção negada |
| **C4** Validação de entrada | CWE-20 | `util/validacao.py` | CPF, e-mail, telefone, senha forte, sanitização |

### A3 / B3 — anti-spoofing por **origem** da chamada (CWE-290)

`realizar_adocao(animal_id, tutor_id, sessao)` **exige** um objeto de sessão
válido. A sessão é criada **apenas** no fluxo autenticado (`auth_controller.autenticar`
chama `util.sessao.iniciar_sessao`) e guarda um token gerado com `secrets`. Um
script externo que importe o controller e chame `realizar_adocao()` diretamente
**não possui** sessão válida e recebe `PermissionError` *antes* de qualquer
escrita. Após o logout (`encerrar_sessao`) o token deixa de valer.

### A2 / B2 — criptografia em repouso (CWE-312)

`dao/database.py` usa **SQLCipher (AES-256)** via `sqlcipher3` quando a
biblioteca está instalada: o arquivo `abrigo.db` fica cifrado no disco (o
`sqlite3` padrão não consegue abri-lo e não há dados em claro nos bytes). A
chave vem da variável de ambiente `ABRIGO_DB_KEY` (nunca versionada). Onde o
SQLCipher **não** está disponível, o sistema cai automaticamente para
`sqlite3` + `chmod 600`, mantendo a portabilidade — o estado real é exposto na
constante `CIFRAGEM_ATIVA` e impresso no início pela `init_db()`.

---

## Testes

```bash
# Executar a partir de abrigo_animais/
python -m pytest tests/ -v
```

- `test_sql_injection.py` — SQL Injection (B1) nos métodos do `AnimalDAO`.
- `test_adocao_origem.py` — anti-spoofing de origem (A3/B3): import direto sem
  sessão é bloqueado; fluxo autenticado funciona; regras de negócio mantidas.
- `test_cifragem_repouso.py` — criptografia em repouso (A2/B2): arquivo ilegível
  sem a chave e sem dados em claro (pulado se o SQLCipher não estiver instalado).
