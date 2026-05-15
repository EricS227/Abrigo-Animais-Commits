# Sistema de Abrigo de Animais

Trabalho da disciplina **Software Seguro** — PUCPR 2026, Equipe 11.

Sistema de gerenciamento de abrigo de animais com interface de linha de comando (CLI), desenvolvido com foco em requisitos de segurança mapeados via STRIDE e rastreados ao longo de todas as camadas da aplicação.

---

## Pre-requisitos

| Item | Versao minima |
|------|---------------|
| Python | 3.10 |
| bcrypt | 4.0.0 |

Para verificar a versao do Python instalada:

```bash
python --version
```

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/EricS227/Roku-Shichi-Sechs-Sieben.git

# Entre na pasta do projeto
cd Roku-Shichi-Sechs-Sieben/abrigo_animais

# Instale as dependências
pip install -r requirements.txt
```

O arquivo `requirements.txt` contém:

```
bcrypt>=4.0.0
```

---

## Execucao

```bash
# Execute a partir de abrigo_animais/
python main.py
```

O banco de dados `abrigo.db` é criado automaticamente na primeira execução com permissão 600 (somente leitura/escrita pelo dono do arquivo — REQ-B2).

---

## Guia de uso das telas (T1 a T4)

### T1 — Tela Inicial

Primeira tela exibida ao iniciar o sistema.

```
  ╔══════════════════════════════════════════════╗
  ║      SISTEMA DE ABRIGO DE ANIMAIS  v1.0      ║
  ║         PUCPR — Software Seguro 2026         ║
  ╚══════════════════════════════════════════════╝

    [1] Entrar (Login)
    [2] Cadastrar novo usuário
    [0] Sair
```

| Opcao | Acao |
|-------|------|
| 1 | Vai para T3 (Login) |
| 2 | Vai para T2 (Cadastro de usuario) |
| 0 | Encerra o programa |

---

### T2 — Cadastro de Usuario

Cria uma nova conta de operador do abrigo.

**Campos solicitados:**

| Campo | Regra de validacao |
|-------|-------------------|
| Username | 3 a 30 caracteres, apenas letras, numeros e `_` |
| Senha | Minimo 8 caracteres, ao menos 1 letra e 1 numero |
| Confirmacao de senha | Deve ser identica a senha digitada |

**Comportamento de segurança:**
- A senha e exibida oculta no terminal (via `getpass`) — nenhum caractere aparece enquanto o usuario digita.
- A senha e armazenada como hash bcrypt com salt automatico. O texto original nunca e gravado no banco (REQ-C2).
- O cadastro e registrado no log de auditoria (REQ-C3).

**Exemplo de fluxo:**

```
  Username (3–30 chars, letras/números/_): joao_op
  Senha (mín. 8 chars, 1 letra, 1 número):
  Confirme a senha:

  Usuário 'joao_op' cadastrado com sucesso!
```

---

### T3 — Autenticacao (Login)

Valida as credenciais do operador antes de dar acesso ao sistema.

**Campos solicitados:**

| Campo | Observacao |
|-------|-----------|
| Username | Texto livre; comparado contra o banco |
| Senha | Exibida oculta no terminal |

**Comportamento de segurança:**
- Mensagem de erro generica ("Usuário ou senha inválidos") para nao revelar se o username existe (REQ-C1 / STRIDE Spoofing).
- Apos 5 tentativas invalidas consecutivas, a conta e bloqueada por 15 minutos (REQ-C1 / CWE-307).
- O desbloqueio e automatico apos o tempo expirar.
- Cada tentativa e registrada no log de auditoria com o numero da tentativa (REQ-C3).
- Login bem-sucedido reseta o contador de tentativas.

**Exemplo de bloqueio:**

```
  ERRO: Usuário ou senha inválidos. Tentativa 3/5.

  ERRO: Conta bloqueada por 15 minutos após 5 tentativas inválidas.
```

Apos login bem-sucedido, o sistema redireciona para o menu principal.

---

### Menu Principal (apos login)

```
  ╔══════════════════════════════════════════════╗
  ║  Logado como: joao_op                        ║
  ╚══════════════════════════════════════════════╝

    [1] Gerenciar Animais (T4)
    [2] Gerenciar Tutores
    [3] Realizar / Listar Adoções
    [4] Ver logs de auditoria
    [0] Sair (Logout)
```

O logout registra a saida no log de auditoria (REQ-C3).

---

### T4 — Gerenciar Animais

Submenu de CRUD para a entidade principal do sistema.

```
    [1] Cadastrar animal
    [2] Listar animais disponíveis
    [3] Listar todos os animais
    [4] Remover animal
    [0] Voltar
```

**[1] Cadastrar animal**

Campos solicitados: Nome, Especie, Raca, Idade (inteiro positivo), Descricao.

Todas as entradas passam por sanitizacao (remocao de caracteres de controle, limite de tamanho) antes de chegar ao DAO (REQ-B3 / REQ-C4). As queries usam prepared statements com placeholders `?` — nenhuma entrada de usuario e concatenada na SQL (REQ-B1).

```
  Nome: Rex
  Espécie (cachorro/gato/outro): cachorro
  Raça: SRD
  Idade (anos): 3
  Descrição: Amigável e vacinado

  Animal cadastrado: [1] Rex | cachorro | SRD | 3 anos | Disponivel
```

**[2] Listar animais disponiveis**

Exibe apenas os animais com status `adotado = 0`. Nao recebe entrada do usuario — a query usa valor fixo parametrizado.

**[3] Listar todos os animais**

Exibe todos os registros independentemente do status de adocao.

**[4] Remover animal**

Solicita o ID do animal e exige confirmacao antes de executar a exclusao (REQ-A1).

```
  ID do animal a remover: 2
  Confirma remoção do animal id=2? (S/N): S

  Animal removido.
```

---

### Gerenciar Tutores

Submenu para cadastro e listagem dos responsaveis pelas adocoes.

**Campos de cadastro:**

| Campo | Validacao |
|-------|-----------|
| Nome | Texto sanitizado, max 200 chars |
| CPF | Exatamente 11 digitos numericos |
| Telefone | 8 a 15 digitos |
| E-mail | Formato `usuario@dominio.ext` (opcional) |

---

### Realizar / Listar Adocoes

**Realizar adocao:**

1. O sistema exibe a lista de animais disponiveis.
2. O operador informa o ID do animal e o ID do tutor.
3. O sistema solicita confirmacao (REQ-A1):

```
  Você deseja adotar o animal id=1 para o tutor id=3?
  Confirma a adoção? (S/N): S

  Adoção registrada: ...
```

4. O animal e marcado como `adotado = 1` e a adocao e registrada com data.

**Listar adocoes:**

Exibe todas as adocoes com nome do animal e nome do tutor (JOIN entre as tabelas).

---

### Logs de Auditoria

Exibe os ultimos 50 registros do log, em ordem decrescente, com timestamp, usuario responsavel, acao e detalhe.

```
  [2026-05-15T10:32:01] joao_op         | LOGIN_SUCESSO            |
  [2026-05-15T10:31:58] joao_op         | LOGIN_FALHA              | Tentativa 2/5
  [2026-05-15T10:20:44] joao_op         | CADASTRO_ANIMAL          | Rex (id=1)
```

Acoes registradas: `CADASTRO_USUARIO`, `LOGIN_SUCESSO`, `LOGIN_FALHA`, `CONTA_BLOQUEADA`, `CADASTRO_ANIMAL`, `REMOCAO_ANIMAL`, `ADOCAO`, `LOGOUT`.

---

## Testes

Os testes cobrem prevencao contra SQL Injection nos metodos `inserir()` e `listar_disponiveis()` do `AnimalDAO`, usando banco SQLite em memoria para isolamento completo.

```bash
# Executar a partir de abrigo_animais/
python -m pytest tests/test_sql_injection.py -v
```

---

## Requisitos de segurança implementados

| Requisito | Descricao | Onde |
|-----------|-----------|------|
| REQ-A1 | Confirmacao dupla (S/N) antes de operacoes criticas | `view/cli.py` |
| REQ-B1 | Prepared statements com `?` em todas as queries | `dao/` |
| REQ-B2 | Permissao 600 no arquivo `abrigo.db` apos criacao | `dao/database.py` |
| REQ-B3 | Validacao de entradas no controller antes do DAO | `controller/` + `util/validacao.py` |
| REQ-C1 | Bloqueio por 15 min apos 5 tentativas invalidas (CWE-307) | `controller/auth_controller.py` |
| REQ-C2 | Senhas com bcrypt + salt automatico (CWE-916) | `controller/auth_controller.py` |
| REQ-C3 | Log de auditoria para todas as acoes criticas | `dao/log_dao.py` |
| REQ-C4 | Sanitizacao: remove caracteres de controle, limita tamanho | `util/validacao.py` |

---

## Arquitetura

```
abrigo_animais/
├── main.py
├── view/
│   └── cli.py                 # Telas T1-T4 (MVC View)
├── controller/
│   ├── auth_controller.py     # Autenticacao, bloqueio, bcrypt
│   ├── animal_controller.py
│   ├── tutor_controller.py
│   └── adocao_controller.py
├── dao/
│   ├── database.py            # Singleton de conexao + init_db
│   ├── animal_dao.py
│   ├── tutor_dao.py
│   ├── adocao_dao.py
│   ├── usuario_dao.py
│   └── log_dao.py
├── model/
│   ├── animal.py
│   ├── tutor.py
│   ├── adocao.py
│   └── usuario.py
├── util/
│   └── validacao.py
└── tests/
    └── test_sql_injection.py
```

Padroes de projeto: Repository (DAOs), Singleton (`get_connection`), Template Method (`init_db`), MVC.
