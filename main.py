"""Interface de linha de comando do validador AP + ALL.

Exemplos:
    python main.py "GCGAATTCGC#ACGTTGCA"
    python main.py "GCGAATTCGC#ACGTTGCA" --rastro
    python main.py --demo
    python main.py --transicoes
    python main.py                      (modo interativo)
"""

import argparse
import sys

from validador import automato_limitado, automato_pilha, casos
from validador.pipeline import Decisao, Resultado, validar

TITULOS = {
    Decisao.ACEITA: "ACEITA (AP aceitou e ALL aceitou)",
    Decisao.REJEITADA_AP: "REJEITADA pelo AP (ALL não executado)",
    Decisao.REJEITADA_ALL: "REJEITADA pelo ALL (regra sensível ao contexto violada)",
    Decisao.ERRO_ENTRADA: "ERRO DE ENTRADA",
}


def imprimir(entrada: str, rastro: bool) -> Resultado:
    resultado = validar(entrada)
    print(f"Entrada: {entrada!r}")
    print(f"Decisão: {TITULOS[resultado.decisao]}")
    print(f"Detalhe: {resultado.mensagem}")
    if rastro and resultado.ap is not None:
        print("\n--- Rastreamento do AP ---")
        print(automato_pilha.formatar_rastro(resultado.parte_ap, resultado.ap.rastro))
        print(f"({resultado.ap.configuracoes_exploradas} configurações exploradas)")
    if rastro and resultado.all_ is not None:
        print("\n--- Rastreamento do ALL ---")
        print(automato_limitado.formatar_rastro(resultado.all_.rastro))
    return resultado


def demo() -> None:
    cenarios = [c for c in casos.carregar("casos_integracao.csv")][:6]
    for i, caso in enumerate(cenarios, start=1):
        print(f"\n{'=' * 78}\nCenário {i}: {caso['regra']}\n{'=' * 78}")
        imprimir(caso["entrada"], rastro=True)


def interativo() -> None:
    print("Digite sequências no formato  PARTE_AP#PARTE_ALL  (linha vazia encerra).")
    while True:
        try:
            linha = input("> ").strip()
        except EOFError:
            break
        if not linha:
            break
        imprimir(linha, rastro=False)
        print()


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")  # ε, ⊢, ⊣ no console do Windows

    parser = argparse.ArgumentParser(description="Validador em duas etapas: AP (GLC) e ALL (sensível ao contexto).")
    parser.add_argument("entrada", nargs="?", help="sequência no formato PARTE_AP#PARTE_ALL")
    parser.add_argument("-r", "--rastro", action="store_true", help="mostra o rastreamento dos autômatos")
    parser.add_argument("--demo", action="store_true", help="executa os cenários de integração com rastreamento")
    parser.add_argument("--transicoes", action="store_true", help="imprime a especificação formal dos dois autômatos")
    args = parser.parse_args()

    if args.transicoes:
        print(automato_pilha.descrever_transicoes(), end="\n\n")
        print(automato_limitado.descrever_transicoes())
        return 0
    if args.demo:
        demo()
        return 0
    if args.entrada is None:
        interativo()
        return 0
    resultado = imprimir(args.entrada, args.rastro)
    return 2 if resultado.decisao is Decisao.ERRO_ENTRADA else 0


if __name__ == "__main__":
    sys.exit(main())
