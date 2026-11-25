"""Etapa 1: Autômato de Pilha (AP) não determinístico.

Linguagem reconhecida (gerada pela GLC  S -> A S T | T S A | C S G | G S C | A T | T A | C G | G C):

    L1 = { w . rc(w) : w em {A,C,G,T}+ }      (rc = reverso-complementar)

Ideia: a primeira metade é lida empilhando o COMPLEMENTO de cada base; o AP "adivinha"
(transição epsilon) o meio da cadeia e, na segunda metade, cada base lida deve ser igual
ao topo da pilha, que então é removido.

Aceitação: por ESTADO FINAL (qFim) com a entrada consumida por inteiro.
A pilha (topo à esquerda) começa com o marcador de fundo Z.
"""

from collections import deque
from dataclasses import dataclass

from .alfabeto import COMPLEMENTO, SIGMA, validar_simbolos

EPS = "ε"
FUNDO = "Z"
ALFABETO_PILHA = (FUNDO,) + SIGMA

Q0, Q_EMP, Q_DES, Q_FIM = "q0", "qEmp", "qDes", "qFim"
Q_ESPERA = {x: f"q{x}" for x in SIGMA}  # qA, qC, qG, qT: "espero ler x"
ESTADOS = (Q0, Q_EMP, Q_DES) + tuple(Q_ESPERA.values()) + (Q_FIM,)
ESTADO_INICIAL = Q0
ESTADOS_FINAIS = (Q_FIM,)


@dataclass(frozen=True)
class Transicao:
    """delta(estado, entrada, topo) = (novo_estado, empilha). `empilha` substitui o topo
    (topo à esquerda); "" significa apenas desempilhar."""

    estado: str
    entrada: str  # símbolo de SIGMA ou EPS
    topo: str
    novo_estado: str
    empilha: str

    def __str__(self) -> str:
        push = self.empilha if self.empilha else EPS
        return f"δ({self.estado}, {self.entrada}, {self.topo}) = ({self.novo_estado}, {push})"


def construir_transicoes() -> tuple[Transicao, ...]:
    t: list[Transicao] = []
    # 1) primeira base: empilha o complemento sobre o fundo
    for x in SIGMA:
        t.append(Transicao(Q0, x, FUNDO, Q_EMP, COMPLEMENTO[x] + FUNDO))
    # 2) primeira metade: empilha o complemento de cada base lida
    for x in SIGMA:
        for topo in SIGMA:
            t.append(Transicao(Q_EMP, x, topo, Q_EMP, COMPLEMENTO[x] + topo))
    # 3) palpite não determinístico: o meio da cadeia foi atingido
    for topo in SIGMA:
        t.append(Transicao(Q_EMP, EPS, topo, Q_DES, topo))
    # 4) desempilha o topo X e passa a "esperar X" na entrada
    for x in SIGMA:
        t.append(Transicao(Q_DES, EPS, x, Q_ESPERA[x], ""))
    # 5) lê o símbolo esperado (pilha inalterada)
    for x in SIGMA:
        for topo in ALFABETO_PILHA:
            t.append(Transicao(Q_ESPERA[x], x, topo, Q_DES, topo))
    # 6) fundo exposto: nada mais a conferir
    t.append(Transicao(Q_DES, EPS, FUNDO, Q_FIM, ""))
    return tuple(t)


TRANSICOES = construir_transicoes()
_INDICE: dict[tuple[str, str, str], list[Transicao]] = {}
for _tr in TRANSICOES:
    _INDICE.setdefault((_tr.estado, _tr.entrada, _tr.topo), []).append(_tr)


@dataclass(frozen=True)
class Configuracao:
    estado: str
    pos: int  # nº de símbolos já lidos
    pilha: str  # topo à esquerda


@dataclass(frozen=True)
class Passo:
    transicao: Transicao | None  # None na configuração inicial
    configuracao: Configuracao


@dataclass
class ResultadoAP:
    aceita: bool
    rastro: list[Passo]  # caminho aceito, ou ramo mais avançado se rejeitada
    configuracoes_exploradas: int
    motivo: str


LIMITE_CONFIGURACOES = 1_000_000  # salvaguarda; a exploração é finita (ver README)


def _sucessores(cadeia: str, c: Configuracao):
    if not c.pilha:
        return
    topo = c.pilha[0]
    resto = c.pilha[1:]
    entradas = [EPS]
    if c.pos < len(cadeia):
        entradas.append(cadeia[c.pos])
    for entrada in entradas:
        for tr in _INDICE.get((c.estado, entrada, topo), ()):
            nova_pos = c.pos + (0 if entrada == EPS else 1)
            yield tr, Configuracao(tr.novo_estado, nova_pos, tr.empilha + resto)


def executar(cadeia: str) -> ResultadoAP:
    """Simula o AP explorando TODOS os ramos (busca em largura sobre configurações).

    Rejeita quando a fila de configurações se esgota sem que algum ramo alcance
    (estado final, entrada consumida)."""
    validar_simbolos(cadeia)
    inicial = Configuracao(ESTADO_INICIAL, 0, FUNDO)
    pai: dict[Configuracao, tuple[Configuracao | None, Transicao | None]] = {inicial: (None, None)}
    profundidade = {inicial: 0}
    fila = deque([inicial])
    aceita_em: Configuracao | None = None

    while fila:
        atual = fila.popleft()
        if atual.estado in ESTADOS_FINAIS and atual.pos == len(cadeia):
            aceita_em = atual
            break
        for tr, nova in _sucessores(cadeia, atual):
            if nova not in pai:
                if len(pai) >= LIMITE_CONFIGURACOES:
                    raise RuntimeError("Limite de configurações excedido")
                pai[nova] = (atual, tr)
                profundidade[nova] = profundidade[atual] + 1
                fila.append(nova)

    if aceita_em is not None:
        return ResultadoAP(True, _caminho(pai, aceita_em), len(pai), "aceita por estado final com a entrada consumida")

    melhor = max(pai, key=lambda c: (c.pos, profundidade[c]))
    motivo = (
        f"nenhum dos {len(pai)} ramos explorados chegou a {Q_FIM} com a entrada consumida; "
        f"o ramo mais avançado parou em {melhor.estado} (lidos {melhor.pos} de {len(cadeia)})"
    )
    return ResultadoAP(False, _caminho(pai, melhor), len(pai), motivo)


def _caminho(pai, final: Configuracao) -> list[Passo]:
    passos: list[Passo] = []
    c: Configuracao | None = final
    while c is not None:
        anterior, tr = pai[c]
        passos.append(Passo(tr, c))
        c = anterior
    passos.reverse()
    return passos


def formatar_rastro(cadeia: str, rastro: list[Passo]) -> str:
    """Tabela do rastreamento: transição, estado, posição de leitura e pilha (topo à esquerda)."""
    linhas = [f"{'#':>3}  {'transição':<28} {'estado':<6} {'leitura':<{len(cadeia) + 3}} pilha (topo à esquerda)"]
    for i, passo in enumerate(rastro):
        c = passo.configuracao
        leitura = f"{cadeia[:c.pos]}|{cadeia[c.pos:]}"
        pilha = c.pilha if c.pilha else "(vazia)"
        tr = str(passo.transicao) if passo.transicao else "configuração inicial"
        linhas.append(f"{i:>3}  {tr:<28} {c.estado:<6} {leitura:<{len(cadeia) + 3}} {pilha}")
    return "\n".join(linhas)


def descrever_transicoes() -> str:
    cabecalho = (
        f"AP: {len(ESTADOS)} estados {list(ESTADOS)}\n"
        f"Alfabeto de entrada: {list(SIGMA)} | alfabeto da pilha: {list(ALFABETO_PILHA)}\n"
        f"Configuração inicial: ({ESTADO_INICIAL}, entrada completa, pilha = {FUNDO})\n"
        f"Aceitação: estado final {list(ESTADOS_FINAIS)} com a entrada consumida por inteiro\n"
        f"{len(TRANSICOES)} transições:\n"
    )
    return cabecalho + "\n".join(f"  {t}" for t in TRANSICOES)
