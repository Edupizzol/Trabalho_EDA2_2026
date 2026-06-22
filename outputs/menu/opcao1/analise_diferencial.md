# Relatório de Análise Diferencial e Contraste Semântico
Este relatório apresenta uma análise comparativa profunda sobre a topologia e a semântica dos grafos de coocorrência das categorias **GOOD**, **MID** e **BAD** reviews. O objetivo é mapear cientificamente como a estrutura do discurso e a importância de determinados conceitos mudam conforme o nível de satisfação do usuário.

---

## 1. Visão Geral das Redes (MacroAnálise)
Esta seção traz uma análise comparativa da estrutura global das redes. Essas métricas revelam a complexidade, a conectividade e a coesão do ecossistema de palavras de cada faixa de satisfação.

| Métrica Global | GOOD REVIEWS | MID REVIEWS | BAD REVIEWS |
| :--- | :---: | :---: | :---: |
| **Vocabulário Ativo (Nós)** | 294 | 359 | 445 |
| **Associações Distintas (Arestas)** | 793 | 852 | 1212 |
| **Densidade do Grafo** | 0.01841 | 0.01326 | 0.01227 |
| **Coeficiente de Agrupamento Médio** | 0.60828 | 0.61185 | 0.57103 |

### O que esses números significam na prática?
* **Densidade:** Indica a proporção de conexões reais frente às conexões possíveis. Uma densidade maior nas críticas de uma categoria sinaliza um discurso altamente focado e repetitivo (combinações de palavras padronizadas). Uma densidade menor indica que as avaliações são pulverizadas e tocam em assuntos muito variados.
* **Coeficiente de Agrupamento (Clustering Coefficient):** Mede a tendência dos nós de formarem aglomerados fechados ('panelinhas' semânticas). Valores elevados revelam que, quando certas palavras aparecem, elas trazem consigo um bloco previsível e rígido de outros termos associados, indicando contextos textuais muito bem definidos.

---

## 2. Hubs Vocabulares Globais (Interseção Semântica)
### O que significa?
Estes termos pertencem à interseção estrita do **Top 30 de PageRank** de todas as três categorias simultaneamente. Significa que, independentemente da nota da review, a centralidade estrutural dessas palavras na rede de coocorrência permanece massiva.

### Impacto e Interpretação nas Reviews:
Por estarem no núcleo de todas as vertentes emocionais, essas palavras representam a **base estrutural e o domínio do dataset** (ex: substantivos essenciais do produto analisado ou verbos de ação mandatórios). Elas funcionam como *âncoras de contexto*: não carregam polaridade sentimental por si só, mas servem como a espinha dorsal sobre a qual as opiniões (positivas ou negativas) são construídas. Identificá-las é crucial para entender qual é o foco temático comum e inegociável de atenção de todos os usuários.

* **Palavras Compartilhadas (Hubs de Domínio):** dia, entrega, produto, americana, qualidade

---

## 3. Assinaturas Exclusivas de Sentimento (Diferenças Topológicas)
### O que significa?
São palavras que alcançaram relevância crítica (Top 30) **exclusivamente** em uma determinada categoria de review, desaparecendo do topo ou sequer existindo nas vertentes opostas.

### Impacto e Interpretação nas Reviews:
Essas palavras são as verdadeiras **assinaturas emocionais** do comportamento do usuário. Elas isolam os fatores puros que geram extrema satisfação ou profunda frustração: 

* As exclusivas em **GOOD** mapeiam os diferenciais competitivos e os maiores acertos da experiência (recursos que encantam e fidelizam o usuário).
* As exclusivas em **BAD** funcionam como um diagnóstico imediato de falhas críticas, bugs de performance, quebras de expectativa ou pontos de fricção severos na jornada.

### Exclusivas de Críticas Positivas (`GOOD`):
* sinal, expectativa, jogo, acabamento, maravilhoso, único, ótima, espaço, parabéns, super, rápido, câmera, bateria, ótimo, água

### Exclusivas de Críticas Negativas (`BAD`):
* cartão, texto, anúncio, livro, uso, semana, hora, resposta, cabelo, empresa, caso, estorno, americano, péssimo, marca, máquina, troca, tv

---

## 4. Deslocamento de Centralidade (Flutuação de Importância via PageRank)
### O que significa?
Esta métrica monitora termos voláteis: palavras que conseguiram entrar no Top 30 tanto de críticas positivas quanto negativas, mas sofreram uma variação drástica em suas posições de ranking (força de centralidade) com uma variação absoluta (|Δ|) de pelo menos 3 posições.

### Impacto e Interpretação nas Reviews:
Este fenômeno revela o **deslocamento de foco de atenção** guiado pela emoção. Quando um termo apresenta um PageRank muito mais alto nas críticas negativas do que nas positivas, isso indica que, quando o recurso associado àquela palavra falha, ele monopoliza o discurso do usuário e se torna o principal assunto gerador de insatisfação.

A tabela abaixo ordena as palavras pela maior força de deslocamento, evidenciando quais conceitos sofrem a maior metamorfose de relevância dentro do ecossistema estudado:

| Palavra | Posição em GOOD | Posição em BAD | Força do Deslocamento |
| :--- | :---: | :---: | :---: |
| **americana** | #25 | #2 | Δ 23 posições |
| **loja** | #26 | #4 | Δ 22 posições |
| **contato** | #29 | #8 | Δ 21 posições |
| **qualidade** | #5 | #14 | Δ 9 posições |
| **dia** | #6 | #3 | Δ 3 posições |

---

## 5. Acoplamento Forte (Vínculos Semânticos Rígidos)
### O que significa?
Esta análise extrai os pares de nós que possuem o maior peso de aresta absoluto na rede. Enquanto o PageRank mede a importância individual e distribuída de um termo, o acoplamento forte nos dá os **nódulos inquebráveis do discurso** — palavras que praticamente exigem a presença uma da outra quando o usuário expressa sua experiência.

### Impacto e Interpretação nas Reviews:
Isso nos revela os 'combos' contextuais exatos. Em redes de texto, o peso da aresta é a frequência de coocorrência em janelas móveis. Identificar os top 3 pares de cada categoria nos permite ver o núcleo das maiores associações mentais做 pelo usuário:

#### Associações Mais Fortes em GOOD REVIEWS:
1. `produto` ↔ `excelente` (Frequência de Coocorrência: **19**)
2. `entrega` ↔ `prazo` (Frequência de Coocorrência: **16**)
3. `bom` ↔ `produto` (Frequência de Coocorrência: **14**)

#### Associações Mais Fortes em MID REVIEWS:
1. `qualidade` ↔ `produto` (Frequência de Coocorrência: **8**)
2. `produto` ↔ `prazo` (Frequência de Coocorrência: **8**)
3. `panela` ↔ `sao` (Frequência de Coocorrência: **5**)

#### Associações Mais Fortes em BAD REVIEWS:
1. `loja` ↔ `americano` (Frequência de Coocorrência: **12**)
2. `produto` ↔ `entrega` (Frequência de Coocorrência: **11**)
3. `dia` ↔ `produto` (Frequência de Coocorrência: **9**)
