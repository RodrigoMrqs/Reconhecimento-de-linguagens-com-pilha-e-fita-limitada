"""Alfabeto, complemento de bases e validação de símbolos (compartilhado pelos módulos)."""

SIGMA = ("A", "C", "G", "T")
SEPARADOR = "#"
COMPLEMENTO = {"A": "T", "T": "A", "C": "G", "G": "C"}


class EntradaInvalida(ValueError):
    """Entrada com símbolo fora do alfabeto ou com formato inválido."""


def validar_simbolos(cadeia: str, alfabeto=SIGMA) -> None:
    """Levanta EntradaInvalida no primeiro símbolo fora do alfabeto (posição 1-indexada)."""
    for i, simbolo in enumerate(cadeia, start=1):
        if simbolo not in alfabeto:
            validos = ", ".join(alfabeto)
            raise EntradaInvalida(
                f"Símbolo fora do alfabeto de entrada: {simbolo!r} na posição {i}. "
                f"Alfabeto válido: {{{validos}}}."
            )


def reverso_complementar(cadeia: str) -> str:
    """Reverso-complementar de uma cadeia sobre {A,C,G,T} (usado só nos testes e na referência)."""
    return "".join(COMPLEMENTO[s] for s in reversed(cadeia))
