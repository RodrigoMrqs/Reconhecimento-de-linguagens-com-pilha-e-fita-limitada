"""Etapa 2: Autômato Linearmente Limitado (ALL) determinístico.

Linguagem reconhecida:

    L2 = { u em {A,C,G,T}+ : #A = #C = #G = #T }     (qualquer ordem)

Fita: ⊢ c1 ... cn ⊣  (n células graváveis + 2 marcadores de borda fixos). O cabeçote pode
LER os marcadores, mas nunca os sobrescreve nem sai do intervalo [⊢, ⊣].

Algoritmo: a cada rodada marca (X) o primeiro A, depois o primeiro C, o primeiro G e o
primeiro T ainda não marcados, voltando ao início da fita entre as buscas. Se faltar uma
base no meio da rodada -> rejeita. Se acabarem os A, a fita só pode conter X -> aceita.
"""

from dataclasses import dataclass

from .alfabeto import SIGMA, validar_simbolos

ESQ, DIR, MARCA = "⊢", "⊣", "X"
ALFABETO_FITA = SIGMA + (MARCA, ESQ, DIR)
E, D = "L", "R"  # esquerda / direita

Q_INI, Q_NV = "qIni", "qNV"
Q_VOLTA = {x: f"qVolta{x}" for x in SIGMA}
Q_BUSCA = {x: f"qBusca{x}" for x in SIGMA}
Q_CHK, Q_ACC, Q_REJ = "qChk", "qAcc", "qRej"
ESTADOS = (Q_INI, Q_NV) + tuple(Q_VOLTA.values()) + tuple(Q_BUSCA.values()) + (Q_CHK, Q_ACC, Q_REJ)
ESTADO_INICIAL = Q_INI
ESTADOS_PARADA = (Q_ACC, Q_REJ)

# Próxima base a buscar depois de marcar a base x (ciclo A -> C -> G -> T -> A ...)
_PROXIMA = {"A": "C", "C": "G", "G": "T", "T": "A"}

MOTIVOS_REJEICAO = {
    Q_NV: "entrada vazia (o ALL exige ao menos uma base)",
    Q_BUSCA["C"]: "há A sem marca mas faltou um C para formar a rodada (contagens diferentes)",
    Q_BUSCA["G"]: "há A e C sem marca mas faltou um G para formar a rodada (contagens diferentes)",
    Q_BUSCA["T"]: "há A, C e G sem marca mas faltou um T para formar a rodada (contagens diferentes)",
    Q_CHK: "acabaram os A, mas sobraram C, G ou T sem marca (contagens diferentes)",
}


@dataclass(frozen=True)
class Transicao:
    """delta(estado, lido) = (novo_estado, escrito, movimento)."""

    estado: str
    lido: str
    novo_estado: str
    escrito: str
    movimento: str

    def __str__(self) -> str:
        return f"δ({self.estado}, {self.lido}) = ({self.novo_estado}, {self.escrito}, {self.movimento})"


def construir_transicoes() -> tuple[Transicao, ...]:
    t: list[Transicao] = []
    # início: ⊢ -> primeira célula
    t.append(Transicao(Q_INI, ESQ, Q_NV, ESQ, D))
    # a fita precisa ter ao menos uma célula; se sim, volta ao ⊢ para começar a rodada
    t.append(Transicao(Q_NV, DIR, Q_REJ, DIR, E))
    for s in SIGMA:
        t.append(Transicao(Q_NV, s, Q_VOLTA["A"], s, E))
    for x in SIGMA:
        # volta até ⊢ e recomeça a busca por x
        for s in SIGMA + (MARCA,):
            t.append(Transicao(Q_VOLTA[x], s, Q_VOLTA[x], s, E))
        t.append(Transicao(Q_VOLTA[x], ESQ, Q_BUSCA[x], ESQ, D))
        # busca a primeira ocorrência de x sem marca
        for s in tuple(b for b in SIGMA if b != x) + (MARCA,):
            t.append(Transicao(Q_BUSCA[x], s, Q_BUSCA[x], s, D))
        t.append(Transicao(Q_BUSCA[x], x, Q_VOLTA[_PROXIMA[x]], MARCA, E))
        # chegou a ⊣ sem achar x
        fim = Q_CHK if x == "A" else Q_REJ  # sem A: confere se só restam X; sem C/G/T: rejeita
        t.append(Transicao(Q_BUSCA[x], DIR, fim, DIR, E))
    # verificação final: da direita para a esquerda, só pode haver X
    t.append(Transicao(Q_CHK, MARCA, Q_CHK, MARCA, E))
    t.append(Transicao(Q_CHK, ESQ, Q_ACC, ESQ, D))
    for s in SIGMA:
        t.append(Transicao(Q_CHK, s, Q_REJ, s, E))
    return tuple(t)


TRANSICOES = construir_transicoes()
DELTA: dict[tuple[str, str], Transicao] = {(t.estado, t.lido): t for t in TRANSICOES}


@dataclass(frozen=True)
class Configuracao:
    estado: str
    fita: str  # inclui ⊢ e ⊣
    cabecote: int  # índice em `fita`


@dataclass(frozen=True)
class Passo:
    transicao: Transicao | None
    configuracao: Configuracao


@dataclass
class ResultadoALL:
    aceita: bool
    rastro: list[Passo]
    passos: int
    motivo: str


def executar(cadeia: str) -> ResultadoALL:
    """Executa o ALL sobre `cadeia` (n células + 2 marcadores). Sempre termina: cada rodada
    marca 4 células ou para; cada marcação custa no máximo 2(n+2) movimentos."""
    validar_simbolos(cadeia)
    n = len(cadeia)
    fita = [ESQ, *cadeia, DIR]
    estado, cab = ESTADO_INICIAL, 0
    rastro = [Passo(None, Configuracao(estado, "".join(fita), cab))]
    limite = 4 * (n + 2) ** 2 + 16  # cota folgada de passos (apenas salvaguarda)
    anterior = estado

    while estado not in ESTADOS_PARADA:
        lido = fita[cab]
        tr = DELTA.get((estado, lido))
        if tr is None:
            return ResultadoALL(False, rastro, len(rastro) - 1, f"sem transição para ({estado}, {lido})")
        if lido in (ESQ, DIR) and tr.escrito != lido:
            raise RuntimeError("marcadores de borda não podem ser sobrescritos")
        fita[cab] = tr.escrito
        cab += 1 if tr.movimento == D else -1
        if not 0 <= cab < len(fita):
            raise RuntimeError("cabeçote saiu dos marcadores de borda")
        anterior, estado = estado, tr.novo_estado
        rastro.append(Passo(tr, Configuracao(estado, "".join(fita), cab)))
        if len(rastro) > limite:
            raise RuntimeError("limite de passos excedido")

    passos = len(rastro) - 1
    if estado == Q_ACC:
        return ResultadoALL(True, rastro, passos, "aceita: todas as células foram marcadas em rodadas completas A,C,G,T")
    return ResultadoALL(False, rastro, passos, MOTIVOS_REJEICAO.get(anterior, "rejeitada"))


def formatar_rastro(rastro: list[Passo]) -> str:
    """Tabela do rastreamento: transição, estado, fita (cabeçote entre colchetes) e posição."""
    larg = len(rastro[0].configuracao.fita) * 3 + 2
    linhas = [f"{'#':>3}  {'transição':<34} {'estado':<8} {'fita (cabeçote entre [ ])':<{larg}} pos"]
    for i, passo in enumerate(rastro):
        c = passo.configuracao
        celulas = [f"[{s}]" if j == c.cabecote else f" {s} " for j, s in enumerate(c.fita)]
        tr = str(passo.transicao) if passo.transicao else "configuração inicial"
        linhas.append(f"{i:>3}  {tr:<34} {c.estado:<8} {''.join(celulas):<{larg}} {c.cabecote}")
    return "\n".join(linhas)


def descrever_transicoes() -> str:
    cabecalho = (
        f"ALL: {len(ESTADOS)} estados {list(ESTADOS)}\n"
        f"Alfabeto de entrada: {list(SIGMA)} | alfabeto da fita: {list(ALFABETO_FITA)}\n"
        f"Configuração inicial: ({ESTADO_INICIAL}, fita = {ESQ} entrada {DIR}, cabeçote em {ESQ})\n"
        f"Aceita em {Q_ACC}; rejeita em {Q_REJ} ou na ausência de transição\n"
        f"{len(TRANSICOES)} transições:\n"
    )
    return cabecalho + "\n".join(f"  {t}" for t in TRANSICOES)
