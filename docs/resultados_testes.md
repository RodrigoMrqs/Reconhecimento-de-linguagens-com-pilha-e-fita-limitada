# Resultados dos testes

Gerado por `python -m validador.relatorio_testes`.

## Autômato de Pilha (AP) isolado

| # | Entrada | Esperada | Obtida | Regra verificada | OK | Mensagem |
|---|---|---|---|---|---|---|
| 1 | `AT` | ACEITA | ACEITA | w.rc(w) com |w|=1 (caso minimo) | sim |  |
| 2 | `TA` | ACEITA | ACEITA | w.rc(w) com |w|=1 | sim |  |
| 3 | `CG` | ACEITA | ACEITA | w.rc(w) com |w|=1 | sim |  |
| 4 | `GC` | ACEITA | ACEITA | w.rc(w) com |w|=1 | sim |  |
| 5 | `ACGT` | ACEITA | ACEITA | rc(AC)=GT | sim |  |
| 6 | `GAATTC` | ACEITA | ACEITA | sitio EcoRI = reverso-complementar de si mesmo | sim |  |
| 7 | `GGATCC` | ACEITA | ACEITA | sitio BamHI | sim |  |
| 8 | `AAGCTT` | ACEITA | ACEITA | sitio HindIII | sim |  |
| 9 | `CCCGGG` | ACEITA | ACEITA | sitio SmaI | sim |  |
| 10 | `GCGAATTCGC` | ACEITA | ACEITA | w=GCGAA e rc(w)=TTCGC | sim |  |
| 11 | `AAAATTTT` | ACEITA | ACEITA | w=AAAA e rc(w)=TTTT | sim |  |
| 12 | ε (vazia) | REJEITA | REJEITA | entrada vazia (w deve ter ao menos 1 base) | sim |  |
| 13 | `A` | REJEITA | REJEITA | comprimento impar | sim |  |
| 14 | `AA` | REJEITA | REJEITA | A so pareia com T | sim |  |
| 15 | `AC` | REJEITA | REJEITA | A so pareia com T | sim |  |
| 16 | `GG` | REJEITA | REJEITA | G so pareia com C | sim |  |
| 17 | `ACGA` | REJEITA | REJEITA | A (inicio) nao pareia com A (fim) | sim |  |
| 18 | `GGATCG` | REJEITA | REJEITA | G (inicio) nao pareia com G (fim) | sim |  |
| 19 | `GAATTCA` | REJEITA | REJEITA | comprimento impar | sim |  |
| 20 | `GCGAATTGGC` | REJEITA | REJEITA | 3a base G nao pareia com 8a base G | sim |  |

## Autômato Linearmente Limitado (ALL) isolado

| # | Entrada | Esperada | Obtida | Regra verificada | OK | Mensagem |
|---|---|---|---|---|---|---|
| 1 | `ACGT` | ACEITA | ACEITA | #A=#C=#G=#T=1 (caso minimo) | sim |  |
| 2 | `CAGT` | ACEITA | ACEITA | #A=#C=#G=#T=1 (outra ordem) | sim |  |
| 3 | `TGCA` | ACEITA | ACEITA | #A=#C=#G=#T=1 (ordem inversa) | sim |  |
| 4 | `AACCGGTT` | ACEITA | ACEITA | 2 de cada base em blocos | sim |  |
| 5 | `CCGGAATT` | ACEITA | ACEITA | 2 de cada base em blocos | sim |  |
| 6 | `GTCAGTCA` | ACEITA | ACEITA | 2 de cada base intercaladas | sim |  |
| 7 | `ATCGGCTA` | ACEITA | ACEITA | 2 de cada base (palindromo) | sim |  |
| 8 | `ACGTTGCA` | ACEITA | ACEITA | 2 de cada base | sim |  |
| 9 | `ACGTACGT` | ACEITA | ACEITA | 2 de cada base | sim |  |
| 10 | `AAAACCCCGGGGTTTT` | ACEITA | ACEITA | 4 de cada base | sim |  |
| 11 | ε (vazia) | REJEITA | REJEITA | entrada vazia | sim |  |
| 12 | `A` | REJEITA | REJEITA | faltam C G T | sim |  |
| 13 | `ACG` | REJEITA | REJEITA | falta T | sim |  |
| 14 | `AAAA` | REJEITA | REJEITA | faltam C G T | sim |  |
| 15 | `ACGTA` | REJEITA | REJEITA | #A=2 e #C=#G=#T=1 | sim |  |
| 16 | `ACGTACG` | REJEITA | REJEITA | #T=1 e as demais 2 | sim |  |
| 17 | `AACCGGT` | REJEITA | REJEITA | #T=1 e as demais 2 | sim |  |
| 18 | `AACCGGTTT` | REJEITA | REJEITA | #T=3 e as demais 2 | sim |  |
| 19 | `GGGGCCCC` | REJEITA | REJEITA | #A=#T=0 | sim |  |
| 20 | `AAAACCCCGGGGTTT` | REJEITA | REJEITA | #T=3 e as demais 4 | sim |  |

## Fluxo completo (AP + ALL)

| # | Entrada | Esperada | Obtida | Regra verificada | OK | Mensagem |
|---|---|---|---|---|---|---|
| 1 | `GCGAATTCGC#ACGTTGCA` | ACEITA | ACEITA | AP aceita (rc) e ALL aceita (2 de cada base) | sim |  |
| 2 | `GCGAATTGGC#ACGTTGCA` | REJEITADA_AP | REJEITADA_AP | AP rejeita (3a base G nao pareia com G); ALL nao executa | sim |  |
| 3 | `GCGAATTCGC#ACGTTGCAA` | REJEITADA_ALL | REJEITADA_ALL | AP aceita; ALL rejeita (#A=3 e as demais 2) | sim |  |
| 4 | `GGATCC#AACCGGTTAACCGGTT` | ACEITA | ACEITA | AP aceita (BamHI) e ALL aceita (4 de cada base) | sim |  |
| 5 | `CCCGGG#ACGTACGTACG` | REJEITADA_ALL | REJEITADA_ALL | AP aceita (SmaI); ALL rejeita (#T=2 e as demais 3) | sim |  |
| 6 | `GCGAAUUCGC#ACGTTGCA` | ERRO_ENTRADA | ERRO_ENTRADA | simbolo U fora do alfabeto {A;C;G;T;#} | sim | Símbolo fora do alfabeto de entrada: 'U' na posição 6. Alfabeto válido: {A, C, G, T, #}. |
| 7 | `GCGAATTCGC` | ERRO_ENTRADA | ERRO_ENTRADA | separador # ausente | sim | Formato inválido: a entrada deve conter exatamente um separador '#' (encontrados: 0). |
| 8 | `GCGAATTCGC#ACGT#ACGT` | ERRO_ENTRADA | ERRO_ENTRADA | mais de um separador # | sim | Formato inválido: a entrada deve conter exatamente um separador '#' (encontrados: 2). |
| 9 | `GCGAATTCGC#ACGTacgt` | ERRO_ENTRADA | ERRO_ENTRADA | minusculas fora do alfabeto | sim | Símbolo fora do alfabeto de entrada: 'a' na posição 16. Alfabeto válido: {A, C, G, T, #}. |
| 10 | `#ACGT` | REJEITADA_AP | REJEITADA_AP | parte do AP vazia | sim |  |
| 11 | `GCGAATTCGC#` | REJEITADA_ALL | REJEITADA_ALL | AP aceita; parte do ALL vazia | sim |  |

**Total: 51 casos, 51 corretos, 0 divergentes.**
