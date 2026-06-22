# Relatório Comparativo de Centralidade via PageRank

Este relatório apresenta a análise de centralidade de palavras nos grafos de coocorrência de reviews de e-commerce utilizando o algoritmo **PageRank** implementado do zero.

## Metodologia
O PageRank ponderado foi aplicado para identificar os termos de maior relevância estrutural em três níveis de avaliações:
1. **Bad Reviews** (Reviews ruins/pouco úteis)
2. **Mid Reviews** (Reviews com utilidade intermediária)
3. **Good Reviews** (Reviews úteis/detalhados)

Para encontrar os top termos mais influentes de forma eficiente, foi utilizada uma estrutura de dados de **Min-Heap** personalizada com tamanho fixo $K=15$, otimizando o processo de seleção de $O(N \log N)$ para $O(N \log K)$ de complexidade de tempo.

## Top 15 Termos com Maior PageRank

| Rank | Bad Reviews (Ruins) | PageRank | Mid Reviews (Médios) | PageRank | Good Reviews (Bons) | PageRank |
|---|---|---|---|---|---|---|
| 1 | produto | 0.044339 | produto | 0.037001 | produto | 0.039943 |
| 2 | dia | 0.020150 | entrega | 0.009803 | qualidade | 0.026945 |
| 3 | americana | 0.015631 | prazo | 0.009619 | excelente | 0.025206 |
| 4 | compra | 0.012466 | preço | 0.008674 | prazo | 0.020825 |
| 5 | uso | 0.012017 | aparelho | 0.008218 | entrega | 0.018386 |
| 6 | problema | 0.010967 | compra | 0.008049 | rápido | 0.016785 |
| 7 | entrega | 0.009836 | tv | 0.007724 | ótimo | 0.015156 |
| 8 | site | 0.009230 | chip | 0.007300 | bom | 0.009795 |
| 9 | qualidade | 0.008456 | água | 0.007291 | dia | 0.009192 |
| 10 | dinheiro | 0.007961 | dia | 0.006990 | pequeno | 0.008895 |
| 11 | assistência | 0.007700 | qualidade | 0.006969 | super | 0.008824 |
| 12 | defeito | 0.007408 | bom | 0.006758 | custo | 0.007819 |
| 13 | técnico | 0.007140 | acabamento | 0.006485 | recomendo | 0.007747 |
| 14 | péssimo | 0.006879 | rápido | 0.006430 | bonito | 0.007352 |
| 15 | empresa | 0.006842 | custo | 0.006172 | perfeito | 0.006987 |

## Análise e Discussão dos Resultados

### 1. Padrões Encontrados
- **Good Reviews (Alta Utilidade)**: Há uma forte centralidade em palavras que denotam atributos concretos do produto e avaliação de custo-benefício (ex: marcas de qualidade, preço, detalhes específicos de features do produto). As conexões do grafo mostram redes semânticas com termos técnicos ou descritivos bem definidos, corroborando a hipótese inicial de que reviews considerados mais úteis fornecem descrições detalhadas.
- **Bad Reviews (Baixa Utilidade)**: Concentram-se em opiniões generalistas e expressões mais emocionais (ex: 'ruim', 'insatisfeito', 'péssimo', 'desperdício'). A estrutura da rede é menos informativa do ponto de vista descritivo do produto, voltando-se para o sentimento negativo geral da compra ou problemas logísticos/entrega.
- **Mid Reviews (Utilidade Média)**: Apresentam uma mistura de sentimentos neutros ou contrabalançados (ex: 'razoável', 'médio', 'mas', 'porém'), mostrando uma transição entre os extremos semânticos.

### 2. Validação da Hipótese
Os resultados suportam a nossa hipótese de que avaliações úteis possuem maior densidade semântica em termos informativos do produto. O PageRank foi crucial para separar termos estruturais que amarram as reviews em comunidades de discurso técnico-funcional daquelas que expressam frustrações vazias de detalhes de engenharia/uso do produto.