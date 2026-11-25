"""Fluxo completo: valida o formato, roda o AP e, se aceitar, roda o ALL."""

from dataclasses import dataclass
from enum import Enum

from . import automato_limitado, automato_pilha
from .alfabeto import SEPARADOR, SIGMA, EntradaInvalida, validar_simbolos


class Decisao(str, Enum):
    ACEITA = "ACEITA"
    REJEITADA_AP = "REJEITADA_AP"
    REJEITADA_ALL = "REJEITADA_ALL"
    ERRO_ENTRADA = "ERRO_ENTRADA"


@dataclass
class Resultado:
    decisao: Decisao
    mensagem: str
    parte_ap: str = ""
    parte_all: str = ""
    ap: automato_pilha.ResultadoAP | None = None
    all_: automato_limitado.ResultadoALL | None = None


def validar(entrada: str) -> Resultado:
    """Entrada esperada:  <palíndromo reverso-complementar> # <sequência com bases balanceadas>."""
    try:
        validar_simbolos(entrada, SIGMA + (SEPARADOR,))
    except EntradaInvalida as erro:
        return Resultado(Decisao.ERRO_ENTRADA, str(erro))
    if entrada.count(SEPARADOR) != 1:
        return Resultado(
            Decisao.ERRO_ENTRADA,
            f"Formato inválido: a entrada deve conter exatamente um separador '{SEPARADOR}' "
            f"(encontrados: {entrada.count(SEPARADOR)}).",
        )

    parte_ap, parte_all = entrada.split(SEPARADOR)
    res_ap = automato_pilha.executar(parte_ap)
    if not res_ap.aceita:
        return Resultado(
            Decisao.REJEITADA_AP,
            f"AP rejeitou '{parte_ap}': {res_ap.motivo}. O ALL não foi executado.",
            parte_ap, parte_all, res_ap,
        )

    res_all = automato_limitado.executar(parte_all)
    if not res_all.aceita:
        return Resultado(
            Decisao.REJEITADA_ALL,
            f"AP aceitou '{parte_ap}', mas o ALL rejeitou '{parte_all}': {res_all.motivo}.",
            parte_ap, parte_all, res_ap, res_all,
        )
    return Resultado(
        Decisao.ACEITA,
        f"AP aceitou '{parte_ap}' e ALL aceitou '{parte_all}'.",
        parte_ap, parte_all, res_ap, res_all,
    )
