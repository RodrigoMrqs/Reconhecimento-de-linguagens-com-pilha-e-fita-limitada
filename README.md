# Validador de sequências de DNA com AP e ALL

Trabalho prático de Linguagens Formais e Autômatos. Equipe: Rodrigo Marques, Pedro Marques e Noam Coelho.

A entrada tem o formato `PARTE_AP # PARTE_ALL` sobre o alfabeto {A, C, G, T} mais o separador `#`. A validação ocorre em duas etapas:

| Etapa | Autômato | Linguagem | Classe |
|---|---|---|---|
| 1 | Autômato de Pilha (não determinístico) | L1 = { w · rc(w) : w ∈ {A,C,G,T}⁺ }, palíndromos reverso-complementares (sítios como EcoRI `GAATTC` e BamHI `GGATCC`) | livre de contexto, não regular |
| 2 | Autômato Linearmente Limitado (determinístico) | L2 = { u ∈ {A,C,G,T}⁺ : #A = #C = #G = #T }, em qualquer ordem | sensível ao contexto, não livre de contexto |

O ALL só executa se o AP aceitar e recebe apenas o trecho após `#`.

**GLC de L1:** `S → A S T | T S A | C S G | G S C | A T | T A | C G | G C`

## Requisitos
Python 3.10 ou superior. Não há dependências externas (`requirements.txt` está vazio de propósito).

## Como executar
```bash
python main.py "GCGAATTCGC#ACGTTGCA"          # valida uma entrada
python main.py "GCGAATTCGC#ACGTTGCA" --rastro  # com rastreamento do AP e do ALL
python main.py --demo                          # cenários de integração com rastreamento
python main.py --transicoes                    # especificação formal dos dois autômatos
python main.py                                 # modo interativo
```
Códigos de saída: 0 (decisão tomada) e 2 (erro de entrada, como símbolo fora do alfabeto).

## Como repetir os testes
```bash
python -m unittest                        # 29 testes (cerca de 9 s)
python -m validador.relatorio_testes      # gera docs/resultados_testes.md
```
Os casos ficam em `dados/` (`casos_ap.csv`, `casos_all.csv`, `casos_integracao.csv`) com entrada, decisão esperada e regra verificada. O relatório acrescenta a decisão obtida de cada um.
Os testes também comparam cada autômato com a definição direta da linguagem em **todas** as cadeias de até 8 símbolos.

## Estrutura
```
main.py                         interface de linha de comando
validador/alfabeto.py           alfabeto, complemento, validação de símbolos
validador/automato_pilha.py     AP: 8 estados, 49 transições, aceitação por estado final
validador/automato_limitado.py  ALL: 13 estados, fita ⊢ u ⊣, aceita em qAcc
validador/pipeline.py           fluxo AP -> ALL e mensagens de erro
validador/relatorio_testes.py   gera a tabela de resultados
dados/                          casos de teste (CSV)
tests/                          testes unitários e de integração
docs/resultados_testes.md       resultados gerados
```

## Decisões de modelagem
- **AP:** empilha o **complemento** de cada base da primeira metade. Um palpite não determinístico (transição ε de `qEmp` para `qDes`) marca o meio. Na segunda metade, cada base lida deve ser igual ao topo da pilha. Aceita em `qFim` com a entrada consumida por inteiro. O simulador faz busca em largura sobre as configurações `(estado, posição, pilha)` e rejeita quando a fila se esgota sem que algum ramo aceite.
- **ALL:** a cada rodada marca com `X` o primeiro A, depois C, G e T sem marca. A fita tem n células mais os marcadores ⊢ e ⊣, que nunca são sobrescritos. O cabeçote nunca sai deles. O simulador verifica isso a cada passo.

## Por que o programa termina
- **AP:** cada transição consome um símbolo, exceto o palpite `qEmp → qDes`, que é irreversível, e o desempilhar `qDes → qX`, que reduz a pilha. A pilha tem no máximo n+1 símbolos, então o número de configurações alcançáveis é finito e a busca esgota a fila.
- **ALL:** cada rodada marca 4 células ou para. Cada marcação custa no máximo 2(n+2) movimentos, então o total é O(n²) passos, e a fita é finita.

## Limitações
- O AP exige que a parte inteira seja o palíndromo. Ele não procura o sítio dentro de uma sequência maior.
- Enzimas reais têm sítios de tamanho fixo (4 a 8 bases). Aqui qualquer palíndromo par é aceito.
- L2 (bases em quantidades iguais) é um critério de composição balanceada, não a regra de Chargaff, que exige apenas A=T e C=G.
- A busca em largura do AP é polinomial nesta linguagem, mas o simulador guarda todas as configurações visitadas na memória.

## Fontes e uso de IA
- Teoria: Sipser, *Introdução à Teoria da Computação*, e Hopcroft, Motwani e Ullman, *Introdução à Teoria dos Autômatos, Linguagens e Computação*. Lema do bombeamento para linguagens regulares e livres de contexto.
- Biologia: sítios de restrição palindrômicos (EcoRI, BamHI, HindIII, SmaI).
- **Uso de IA:**
  - **Ferramenta:** Claude Code (Anthropic), modelo Claude Sonnet 5.5.
  - **Tarefas apoiadas:** auxílio na estruturação do código (organização dos módulos, simuladores, testes e README) e consultoria para otimização e correção (por exemplo, a correção de um caso de teste que estava errado).
  - **O que a equipe verificou:** validação das correções e otimizações sugeridas pelo modelo de inteligência artificial e implementação das que condiziam com o objetivo do projeto.
