import itertools
import unittest

from validador import automato_pilha as ap
from validador import casos
from validador.alfabeto import SIGMA, EntradaInvalida, reverso_complementar


def referencia(cadeia: str) -> bool:
    """Definição direta da linguagem: w . rc(w), com |w| >= 1."""
    meio = len(cadeia) // 2
    return len(cadeia) >= 2 and len(cadeia) % 2 == 0 and cadeia[meio:] == reverso_complementar(cadeia[:meio])


class TestEspecificacao(unittest.TestCase):
    def test_pelo_menos_oito_estados(self):
        self.assertGreaterEqual(len(ap.ESTADOS), 8)

    def test_transicoes_so_usam_estados_declarados(self):
        for t in ap.TRANSICOES:
            self.assertIn(t.estado, ap.ESTADOS)
            self.assertIn(t.novo_estado, ap.ESTADOS)


class TestCasosDoCsv(unittest.TestCase):
    def setUp(self):
        self.casos = casos.carregar("casos_ap.csv")

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
                self.assertEqual(ap.executar(c["entrada"]).aceita, esperado, c["regra"])


class TestEquivalenciaExaustiva(unittest.TestCase):
    def test_todas_as_cadeias_ate_comprimento_8(self):
        for n in range(0, 9):
            for tupla in itertools.product(SIGMA, repeat=n):
                cadeia = "".join(tupla)
                self.assertEqual(ap.executar(cadeia).aceita, referencia(cadeia), cadeia)


class TestRastroEComportamento(unittest.TestCase):
    def test_rastro_da_cadeia_aceita(self):
        r = ap.executar("GCGAATTCGC")
        self.assertTrue(r.aceita)
        final = r.rastro[-1].configuracao
        self.assertEqual((final.estado, final.pos, final.pilha), ("qFim", 10, ""))
        pico = max(len(p.configuracao.pilha) for p in r.rastro)
        self.assertEqual(pico, 6)  # 5 complementos empilhados + fundo Z
        self.assertEqual(r.rastro[0].configuracao.pilha, "Z")

    def test_rastro_empilha_complementos(self):
        r = ap.executar("AT")
        self.assertEqual([p.configuracao.pilha for p in r.rastro][:3], ["Z", "TZ", "TZ"])

    def test_nao_determinismo_explora_varios_ramos(self):
        # "AATT" tem ramos que apostam em meios errados; todos precisam ser explorados e descartados.
        r = ap.executar("AATT")
        self.assertTrue(r.aceita)
        self.assertGreater(r.configuracoes_exploradas, len(r.rastro))

    def test_rejeicao_informa_motivo(self):
        r = ap.executar("AA")
        self.assertFalse(r.aceita)
        self.assertIn("nenhum", r.motivo)

    def test_simbolo_fora_do_alfabeto(self):
        with self.assertRaises(EntradaInvalida):
            ap.executar("GCU")

    def test_termina_em_entrada_longa(self):
        cadeia = "AACG" * 25  # rc(AACG) = CGTT, logo cadeia+cadeia não é w.rc(w)
        self.assertTrue(ap.executar(cadeia + reverso_complementar(cadeia)).aceita)
        self.assertFalse(ap.executar(cadeia + cadeia).aceita)


if __name__ == "__main__":
    unittest.main()
