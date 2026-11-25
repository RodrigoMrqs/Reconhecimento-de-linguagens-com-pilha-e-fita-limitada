"""Executa os casos de dados/*.csv e registra entrada, decisão esperada, decisão obtida e regra.

Uso:  python -m validador.relatorio_testes      (gera docs/resultados_testes.md)
"""

import sys
from pathlib import Path

from . import automato_limitado, automato_pilha, casos
from .pipeline import validar

SAIDA = Path(__file__).resolve().parent.parent / "docs" / "resultados_testes.md"


def _fmt(entrada: str) -> str:
    return f"`{entrada}`" if entrada else "ε (vazia)"


def _obtida_ap(entrada: str) -> tuple[str, str]:
    return ("ACEITA" if automato_pilha.executar(entrada).aceita else "REJEITA"), ""


def _obtida_all(entrada: str) -> tuple[str, str]:
    return ("ACEITA" if automato_limitado.executar(entrada).aceita else "REJEITA"), ""


def _obtida_integracao(entrada: str) -> tuple[str, str]:
    r = validar(entrada)
    return r.decisao.value, (r.mensagem if r.decisao.value == "ERRO_ENTRADA" else "")


SECOES = (
    ("Autômato de Pilha (AP) isolado", "casos_ap.csv", _obtida_ap),
    ("Autômato Linearmente Limitado (ALL) isolado", "casos_all.csv", _obtida_all),
    ("Fluxo completo (AP + ALL)", "casos_integracao.csv", _obtida_integracao),
)


def gerar() -> tuple[str, int, int]:
    linhas = ["# Resultados dos testes", "", "Gerado por `python -m validador.relatorio_testes`.", ""]
    total = falhas = 0
    for titulo, arquivo, obter in SECOES:
        linhas += [f"## {titulo}", "", "| # | Entrada | Esperada | Obtida | Regra verificada | OK | Mensagem |", "|---|---|---|---|---|---|---|"]
        for i, caso in enumerate(casos.carregar(arquivo), start=1):
            obtida, mensagem = obter(caso["entrada"])
            ok = obtida == caso["esperado"]
            total += 1
            falhas += not ok
            linhas.append(
                f"| {i} | {_fmt(caso['entrada'])} | {caso['esperado']} | {obtida} | {caso['regra']} | "
                f"{'sim' if ok else '**NÃO**'} | {mensagem} |"
            )
        linhas.append("")
    linhas.append(f"**Total: {total} casos, {total - falhas} corretos, {falhas} divergentes.**")
    return "\n".join(linhas) + "\n", total, falhas


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    texto, total, falhas = gerar()
    SAIDA.parent.mkdir(exist_ok=True)
    SAIDA.write_text(texto, encoding="utf-8")
    print(f"{total} casos executados, {falhas} divergentes. Relatório: {SAIDA}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
