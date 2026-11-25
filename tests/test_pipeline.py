import unittest

from validador import casos
from validador.pipeline import Decisao, validar


class TestFluxoCompleto(unittest.TestCase):
    def test_casos_do_csv(self):
        for c in casos.carregar("casos_integracao.csv"):
            with self.subTest(entrada=c["entrada"]):
                self.assertEqual(validar(c["entrada"]).decisao.value, c["esperado"], c["regra"])

    def test_tres_cenarios_obrigatorios_com_18_caracteres_ou_mais(self):
        aceita = validar("GCGAATTCGC#ACGTTGCA")
        rej_ap = validar("GCGAATTGGC#ACGTTGCA")
        rej_all = validar("GCGAATTCGC#ACGTTGCAA")
        self.assertEqual(aceita.decisao, Decisao.ACEITA)
        self.assertEqual(rej_ap.decisao, Decisao.REJEITADA_AP)
        self.assertEqual(rej_all.decisao, Decisao.REJEITADA_ALL)
        for entrada in ("GCGAATTCGC#ACGTTGCA", "GCGAATTGGC#ACGTTGCA", "GCGAATTCGC#ACGTTGCAA"):
            self.assertGreaterEqual(len(entrada), 18)

    def test_all_nao_executa_quando_ap_rejeita(self):
        r = validar("GCGAATTGGC#ACGTTGCA")
        self.assertIsNotNone(r.ap)
        self.assertIsNone(r.all_)

    def test_all_executa_so_com_a_parte_apos_o_separador(self):
        r = validar("GCGAATTCGC#ACGTTGCA")
        self.assertEqual(r.parte_all, "ACGTTGCA")
        self.assertEqual(r.all_.rastro[0].configuracao.fita, "⊢ACGTTGCA⊣")

    def test_simbolo_fora_do_alfabeto_mostra_mensagem(self):
        r = validar("GCGAAUUCGC#ACGTTGCA")
        self.assertEqual(r.decisao, Decisao.ERRO_ENTRADA)
        self.assertEqual(
            r.mensagem,
            "Símbolo fora do alfabeto de entrada: 'U' na posição 6. Alfabeto válido: {A, C, G, T, #}.",
        )

    def test_formato_sem_separador(self):
        r = validar("GCGAATTCGC")
        self.assertEqual(r.decisao, Decisao.ERRO_ENTRADA)
        self.assertIn("exatamente um separador", r.mensagem)


if __name__ == "__main__":
    unittest.main()
