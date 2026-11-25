import itertools
import unittest

from validador import automato_limitado as al
from validador import casos
from validador.alfabeto import SIGMA, EntradaInvalida


def referencia(cadeia: str) -> bool:
    """Definição direta da linguagem: #A = #C = #G = #T e |u| >= 1."""
    return len(cadeia) > 0 and len({cadeia.count(b) for b in SIGMA}) == 1


class TestEspecificacao(unittest.TestCase):
    def test_pelo_menos_oito_estados(self):
        self.assertGreaterEqual(len(al.ESTADOS), 8)

    def test_deterministico(self):
        self.assertEqual(len(al.TRANSICOES), len(al.DELTA))

    def test_marcadores_nunca_sao_sobrescritos(self):
        for t in al.TRANSICOES:
            if t.lido in (al.ESQ, al.DIR):
                self.assertEqual(t.escrito, t.lido)


class TestCasosDoCsv(unittest.TestCase):
    def setUp(self):
        self.casos = casos.carregar("casos_all.csv")

    def test_quantidades_minimas_e_cadeias_distintas(self):
        entradas = [c["entrada"] for c in self.casos]
        self.assertEqual(len(entradas), len(set(entradas)))
        self.assertGreaterEqual(sum(c["esperado"] == "ACEITA" for c in self.casos), 8)
        self.assertGreaterEqual(sum(c["esperado"] == "REJEITA" for c in self.casos), 8)
        self.assertIn("", entradas)  # caso-limite: entrada vazia

    def test_decisoes(self):
        for c in self.casos:
            with self.subTest(entrada=c["entrada"]):
                esperado = c["esperado"] == "ACEITA"
                self.assertEqual(al.executar(c["entrada"]).aceita, esperado, c["regra"])


class TestEquivalenciaExaustiva(unittest.TestCase):
    def test_todas_as_cadeias_ate_comprimento_8(self):
        for n in range(0, 9):
            for tupla in itertools.product(SIGMA, repeat=n):
                cadeia = "".join(tupla)
                self.assertEqual(al.executar(cadeia).aceita, referencia(cadeia), cadeia)


class TestFita(unittest.TestCase):
    def test_cabecote_respeita_bordas_e_fita_tem_n_mais_2_celulas(self):
        for cadeia in ("ACGT", "AACCGGTTT", "GTCAGTCA", "", "A"):
            r = al.executar(cadeia)
            for passo in r.rastro:
                c = passo.configuracao
                self.assertEqual(len(c.fita), len(cadeia) + 2)
                self.assertTrue(c.fita.startswith(al.ESQ) and c.fita.endswith(al.DIR))
                self.assertTrue(0 <= c.cabecote < len(c.fita))

    def test_fita_final_da_cadeia_aceita_so_tem_marcas(self):
        r = al.executar("ACGTTGCA")
        self.assertTrue(r.aceita)
        self.assertEqual(r.rastro[-1].configuracao.fita, "⊢XXXXXXXX⊣")
        self.assertEqual(r.rastro[-1].configuracao.estado, "qAcc")

    def test_configuracao_inicial(self):
        c = al.executar("ACGT").rastro[0].configuracao
        self.assertEqual((c.estado, c.fita, c.cabecote), ("qIni", "⊢ACGT⊣", 0))

    def test_quadratico_no_pior_caso(self):
        for n in (4, 8, 16, 32):
            cadeia = "A" * (n // 4) + "C" * (n // 4) + "G" * (n // 4) + "T" * (n // 4)
            self.assertLessEqual(al.executar(cadeia).passos, 4 * (n + 2) ** 2)

    def test_motivo_de_rejeicao(self):
        self.assertIn("vazia", al.executar("").motivo)
        self.assertIn("contagens", al.executar("ACGTA").motivo)

    def test_simbolo_fora_do_alfabeto(self):
        with self.assertRaises(EntradaInvalida):
            al.executar("ACGU")


if __name__ == "__main__":
    unittest.main()
