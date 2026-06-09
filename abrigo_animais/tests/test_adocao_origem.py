"""
tests/test_adocao_origem.py
REQ-A3 / REQ-B3 (CWE-290 — anti-spoofing por ORIGEM da chamada).

Comprova que:
  1. realizar_adocao() por import direto SEM sessão válida é bloqueado (PermissionError);
  2. um objeto de sessão FORJADO (token errado) também é bloqueado;
  3. o fluxo autenticado (sessão real via iniciar_sessao) funciona;
  4. regras de negócio continuam barradas: animal já adotado e IDs inválidos.

Estratégia de isolamento: substitui a conexão Singleton de dao.database por um
banco SQLite em memória com o schema completo. Como TODOS os DAOs chamam
get_connection(), que lê dao.database._connection, basta injetar a conexão lá.
"""

import os
import sqlite3
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import dao.database as database
import controller.adocao_controller as adocao_ctrl
from model.animal import Animal
from model.tutor import Tutor
from dao.animal_dao import AnimalDAO
from dao.tutor_dao import TutorDAO
import util.sessao as sessao


class TestAdocaoOrigem(unittest.TestCase):

    def setUp(self):
        # Banco em memória com o schema do projeto, injetado no Singleton
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        self._conn = conn
        self._conn_original = database._connection
        database._connection = conn
        database.init_db()  # cria tabelas usando a conexão injetada

        # Dados de apoio: 1 animal disponível + 1 tutor
        self.animal_id = AnimalDAO().inserir(
            Animal(nome="Rex", especie="cachorro", raca="SRD",
                   idade=3, descricao="dócil", adotado=False)
        )
        self.tutor_id = TutorDAO().inserir(
            Tutor(nome="Maria", cpf="11144477735",
                  telefone="4133334444", email="maria@x.com")
        )
        # Garante que não há sessão ativa no início de cada teste
        sessao.encerrar_sessao()

    def tearDown(self):
        sessao.encerrar_sessao()
        self._conn.close()
        database._connection = self._conn_original

    # ------------------------------------------------------------------ #
    # REQ-A3: import direto sem sessão -> bloqueado ANTES de qualquer escrita
    # ------------------------------------------------------------------ #
    def test_import_direto_sem_sessao_e_bloqueado(self):
        with self.assertRaises(PermissionError):
            adocao_ctrl.realizar_adocao(self.animal_id, self.tutor_id)
        # nada foi adotado
        animal = AnimalDAO().buscar_por_id(self.animal_id)
        self.assertFalse(animal.adotado, "Animal foi adotado sem sessão válida!")

    def test_sessao_none_explicito_e_bloqueado(self):
        with self.assertRaises(PermissionError):
            adocao_ctrl.realizar_adocao(self.animal_id, self.tutor_id, sessao=None)

    def test_sessao_forjada_token_invalido_e_bloqueada(self):
        # Há uma sessão ativa legítima...
        sessao.iniciar_sessao("operador")
        # ...mas o atacante tenta passar um objeto forjado com token diferente
        falsa = sessao.Sessao("operador")
        falsa.token = "0" * 32  # token que não bate com o da sessão ativa
        with self.assertRaises(PermissionError):
            adocao_ctrl.realizar_adocao(self.animal_id, self.tutor_id, sessao=falsa)

    def test_objeto_qualquer_como_sessao_e_bloqueado(self):
        sessao.iniciar_sessao("operador")

        class Fake:
            username = "operador"
            token = "qualquer"

        with self.assertRaises(PermissionError):
            adocao_ctrl.realizar_adocao(self.animal_id, self.tutor_id, sessao=Fake())

    # ------------------------------------------------------------------ #
    # Fluxo autenticado: sessão real -> adoção funciona
    # ------------------------------------------------------------------ #
    def test_fluxo_autenticado_funciona(self):
        s = sessao.iniciar_sessao("operador")
        adocao = adocao_ctrl.realizar_adocao(self.animal_id, self.tutor_id, sessao=s)
        self.assertEqual(adocao.animal_id, self.animal_id)
        self.assertEqual(adocao.tutor_id, self.tutor_id)
        animal = AnimalDAO().buscar_por_id(self.animal_id)
        self.assertTrue(animal.adotado, "Animal não foi marcado como adotado")

    # ------------------------------------------------------------------ #
    # REQ-B3: regras de negócio continuam barradas (com sessão válida)
    # ------------------------------------------------------------------ #
    def test_animal_ja_adotado_e_barrado(self):
        s = sessao.iniciar_sessao("operador")
        adocao_ctrl.realizar_adocao(self.animal_id, self.tutor_id, sessao=s)
        with self.assertRaises(ValueError):
            adocao_ctrl.realizar_adocao(self.animal_id, self.tutor_id, sessao=s)

    def test_id_nao_inteiro_e_barrado(self):
        s = sessao.iniciar_sessao("operador")
        with self.assertRaises(ValueError):
            adocao_ctrl.realizar_adocao("abc", self.tutor_id, sessao=s)

    def test_animal_inexistente_e_barrado(self):
        s = sessao.iniciar_sessao("operador")
        with self.assertRaises(ValueError):
            adocao_ctrl.realizar_adocao(99999, self.tutor_id, sessao=s)

    def test_origem_verificada_antes_do_negocio(self):
        # Sem sessão, mesmo com IDs inexistentes deve dar PermissionError
        # (origem é checada ANTES da validação de negócio), não ValueError.
        with self.assertRaises(PermissionError):
            adocao_ctrl.realizar_adocao(99999, 88888)


if __name__ == "__main__":
    unittest.main(verbosity=2)
