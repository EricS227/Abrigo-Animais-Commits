"""
tests/test_cifragem_repouso.py
REQ-A2 / REQ-B2 — Proteção de dados em repouso (CWE-312).

Comprova que, quando o SQLCipher está disponível (CIFRAGEM_ATIVA), o banco
gravado em disco fica realmente cifrado:
  - o sqlite3 padrão NÃO consegue abrir o arquivo;
  - dados sensíveis NÃO aparecem em claro nos bytes do arquivo;
  - com a chave correta os dados são lidos; com a chave errada, falha.

Onde o SQLCipher não está instalado, os testes são pulados (a mitigação
efetiva passa a ser chmod 600, validada operacionalmente, não aqui).
"""

import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dao.database import CIFRAGEM_ATIVA


@unittest.skipUnless(CIFRAGEM_ATIVA, "SQLCipher indisponível neste ambiente")
class TestCifragemRepouso(unittest.TestCase):

    def setUp(self):
        import sqlcipher3.dbapi2 as driver
        self.driver = driver
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "cofre.db")
        self.KEY = "chave-secreta-teste"

        con = driver.connect(self.path)
        con.execute(f"PRAGMA key = '{self.KEY}'")
        con.execute("CREATE TABLE segredo(valor TEXT)")
        con.execute("INSERT INTO segredo VALUES ('DADO_SENSIVEL_LGPD')")
        con.commit()
        con.close()

    def tearDown(self):
        try:
            os.remove(self.path)
            os.rmdir(self.dir)
        except OSError:
            pass

    def test_arquivo_nao_e_legivel_pelo_sqlite_padrao(self):
        with self.assertRaises(sqlite3.DatabaseError):
            sqlite3.connect(self.path).execute("SELECT * FROM segredo").fetchall()

    def test_dado_sensivel_nao_aparece_em_claro_no_disco(self):
        raw = open(self.path, "rb").read()
        self.assertNotIn(b"DADO_SENSIVEL_LGPD", raw)
        # Banco SQLite em claro começa com este magic header; o cifrado, não.
        self.assertFalse(raw.startswith(b"SQLite format 3"))

    def test_leitura_com_chave_correta(self):
        con = self.driver.connect(self.path)
        con.execute(f"PRAGMA key = '{self.KEY}'")
        rows = con.execute("SELECT valor FROM segredo").fetchall()
        con.close()
        self.assertEqual(rows[0][0], "DADO_SENSIVEL_LGPD")

    def test_chave_errada_e_rejeitada(self):
        con = self.driver.connect(self.path)
        con.execute("PRAGMA key = 'chave-errada'")
        with self.assertRaises(self.driver.DatabaseError):
            con.execute("SELECT * FROM segredo").fetchall()
        con.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
