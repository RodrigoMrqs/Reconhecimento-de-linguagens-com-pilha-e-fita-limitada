"""Carrega os casos de teste de dados/*.csv (colunas: entrada, esperado, regra)."""

import csv
from pathlib import Path

DIRETORIO_DADOS = Path(__file__).resolve().parent.parent / "dados"


def carregar(nome: str) -> list[dict[str, str]]:
    with open(DIRETORIO_DADOS / nome, newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))
