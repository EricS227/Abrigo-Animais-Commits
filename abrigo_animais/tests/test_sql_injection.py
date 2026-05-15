"""
tests/test_sql_injection.py
Verifica que AnimalDAO usa Prepared Statements em todos os métodos,
impedindo SQL Injection via sanitização automática do driver sqlite3.

Critérios cobertos:
  - Placeholders (?) em INSERT e SELECT (REQ-B1)
  - Zero concatenação de strings com entrada do usuário
  - listar_disponiveis() e inserir() confirmados contra payloads reais
"""

import sqlite3
import sys
import os
import unittest
from unittest.mock import patch

# Garante que 'abrigo_animais/' está no path ao rodar de qualquer diretório
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from model.animal import Animal
from dao.animal_dao import AnimalDAO


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _criar_banco_memoria() -> sqlite3.Connection:
    """Banco SQLite em memória com o schema da tabela animal."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE animal (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT    NOT NULL,
            especie   TEXT    NOT NULL,
            raca      TEXT,
            idade     INTEGER,
            descricao TEXT,
            adotado   INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


def _tabela_animal_existe(conn: sqlite3.Connection) -> bool:
    """Verifica se a tabela 'animal' ainda existe (detecta DROP TABLE injetado)."""
    row = conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='animal'"
    ).fetchone()
    return row[0] == 1


# --------------------------------------------------------------------------- #
# Suite de testes
# --------------------------------------------------------------------------- #

class TestAnimalDAOSQLInjection(unittest.TestCase):
    """
    Cada teste injeta um payload clássico de SQL Injection em um campo
    e verifica que:
      1. O banco continua íntegro (nenhuma tabela foi dropada/alterada).
      2. O valor é persistido/retornado literalmente como string, não executado.
    """

    def setUp(self):
        self.conn = _criar_banco_memoria()
        # Substitui get_connection() pelo banco em memória isolado
        self.patcher = patch("dao.animal_dao.get_connection",
                             return_value=self.conn)
        self.patcher.start()
        self.dao = AnimalDAO()

    def tearDown(self):
        self.patcher.stop()
        self.conn.close()

    # ------------------------------------------------------------------ #
    # inserir() — payloads de injeção devem ser dados, não comandos SQL
    # ------------------------------------------------------------------ #

    def test_inserir_payload_drop_table_no_nome(self):
        """
        Payload clássico 'DROP TABLE' no campo nome:
        a tabela deve continuar existindo e o nome ser salvo literalmente.
        """
        payload = "Rex'; DROP TABLE animal; --"
        animal = Animal(nome=payload, especie="Cachorro",
                        raca="SRD", idade=2, descricao="", adotado=False)

        animal_id = self.dao.inserir(animal)

        # Tabela não foi dropada
        self.assertTrue(_tabela_animal_existe(self.conn),
                        "A tabela 'animal' foi removida — injeção bem-sucedida!")

        # Registro salvo com o nome exato (string literal)
        row = self.conn.execute(
            "SELECT nome FROM animal WHERE id = ?", (animal_id,)
        ).fetchone()
        self.assertIsNotNone(row, "Registro não encontrado após inserir()")
        self.assertEqual(row["nome"], payload)

    def test_inserir_payload_union_select_na_descricao(self):
        """
        Payload UNION SELECT em descricao não deve vazar dados de outras tabelas
        nem quebrar a query — o valor é armazenado como texto.
        """
        payload = "' UNION SELECT 1,2,3,4,5,6 --"
        animal = Animal(nome="Bolinha", especie="Gato", raca="Persa",
                        idade=1, descricao=payload, adotado=False)

        animal_id = self.dao.inserir(animal)

        row = self.conn.execute(
            "SELECT descricao FROM animal WHERE id = ?", (animal_id,)
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["descricao"], payload)

    def test_inserir_aspas_simples_nao_quebram_query(self):
        """
        Aspas simples em campos de texto não causam erro de sintaxe SQL.
        O driver sqlite3 escapa automaticamente via binding de parâmetros.
        """
        animal = Animal(nome="O'Malley", especie="Gato", raca="",
                        idade=3, descricao="d'Artagnan's pet", adotado=False)

        animal_id = self.dao.inserir(animal)

        row = self.conn.execute(
            "SELECT nome, descricao FROM animal WHERE id = ?", (animal_id,)
        ).fetchone()
        self.assertEqual(row["nome"], "O'Malley")
        self.assertEqual(row["descricao"], "d'Artagnan's pet")

    def test_inserir_payload_boolean_blindado(self):
        """
        Payload de Boolean-based blind injection no campo raca
        é armazenado como string sem alterar o comportamento da query.
        """
        payload = "' OR '1'='1"
        animal = Animal(nome="Fido", especie="Cachorro", raca=payload,
                        idade=4, descricao="", adotado=False)

        animal_id = self.dao.inserir(animal)

        row = self.conn.execute(
            "SELECT raca FROM animal WHERE id = ?", (animal_id,)
        ).fetchone()
        self.assertEqual(row["raca"], payload)

    # ------------------------------------------------------------------ #
    # listar_disponiveis() — filtro adotado=0 imune a dados maliciosos
    # ------------------------------------------------------------------ #

    def test_listar_disponiveis_retorna_apenas_nao_adotados(self):
        """
        listar_disponiveis() usa WHERE adotado = 0 com parâmetro fixo;
        animais adotados nunca aparecem na listagem.
        """
        self.dao.inserir(Animal(nome="Rex",   especie="Cachorro",
                                raca="", idade=2, adotado=False))
        self.dao.inserir(Animal(nome="Mia",   especie="Gato",
                                raca="", idade=1, adotado=True))   # adotado
        self.dao.inserir(Animal(nome="Bob",   especie="Cachorro",
                                raca="", idade=3, adotado=False))

        disponiveis = self.dao.listar_disponiveis()
        nomes = [a.nome for a in disponiveis]

        self.assertIn("Rex", nomes)
        self.assertIn("Bob", nomes)
        self.assertNotIn("Mia", nomes,
                         "Animal adotado apareceu em listar_disponiveis()")

    def test_listar_disponiveis_payload_no_nome_nao_vaza_adotados(self):
        """
        Mesmo que um animal adotado tenha nome com payload SQL,
        listar_disponiveis() não o retorna — o filtro não é subvertido.
        """
        payload_nome = "1' OR adotado=1 --"
        self.dao.inserir(Animal(nome=payload_nome, especie="Cachorro",
                                raca="", idade=2, adotado=True))
        self.dao.inserir(Animal(nome="Firula", especie="Gato",
                                raca="", idade=1, adotado=False))

        disponiveis = self.dao.listar_disponiveis()
        nomes = [a.nome for a in disponiveis]

        self.assertNotIn(payload_nome, nomes,
                         "Animal adotado vazou via payload no nome")
        self.assertIn("Firula", nomes)

    def test_listar_disponiveis_sem_animais_retorna_lista_vazia(self):
        """listar_disponiveis() retorna lista vazia quando não há animais."""
        resultado = self.dao.listar_disponiveis()
        self.assertEqual(resultado, [])

    def test_listar_disponiveis_todos_adotados_retorna_vazio(self):
        """Se todos os animais estiverem adotados, retorna lista vazia."""
        self.dao.inserir(Animal(nome="Luna", especie="Gato",
                                raca="", idade=2, adotado=True))
        self.dao.inserir(Animal(nome="Thor", especie="Cachorro",
                                raca="", idade=5, adotado=True))

        resultado = self.dao.listar_disponiveis()
        self.assertEqual(resultado, [],
                         "Esperado lista vazia, mas animais adotados foram retornados")


if __name__ == "__main__":
    unittest.main(verbosity=2)
