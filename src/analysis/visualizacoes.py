
import os
import json
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from src.analysis.pagerank import PageRankCalculator
from src.interface.console import exibir_secao, log_info, log_ok, log_aviso, log_erro, log_dados


_CATEGORIAS = ["bad_reviews", "mid_reviews", "good_reviews"]
_LABELS = {"bad_reviews": "BAD", "mid_reviews": "MID", "good_reviews": "GOOD"}
_CORES = {"bad_reviews": "#E74C3C", "mid_reviews": "#F39C12", "good_reviews": "#27AE60"}
_OUTPUT_DIR = os.path.join("outputs", "visualizacoes")


# ── Helpers internos ─────────────────────────────────────────────────────────

def _carregar_grafos():
    """Carrega os 3 grafos JSON. Retorna None se algum não existir."""
    dados = {}
    for cat in _CATEGORIAS:
        path = os.path.join("data", "graphs", f"{cat}_graph.json")
        if not os.path.exists(path):
            log_erro(f"Grafo não encontrado: '{path}'. Execute a Etapa 1 antes.")
            return None
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        dados[cat] = {
            "graph": d["grafo"]["graph"],
            "id_to_word": d["grafo"]["id_to_word"],
        }
    return dados


def _salvar_md(nome_arquivo: str, conteudo: str):
    path = os.path.join(_OUTPUT_DIR, nome_arquivo)
    with open(path, "w", encoding="utf-8") as f:
        f.write(conteudo)


def _salvar_fig(nome_arquivo: str) -> str:
    path = os.path.join(_OUTPUT_DIR, nome_arquivo)
    plt.savefig(path, format="PNG", dpi=130, bbox_inches="tight")
    plt.close()
    return nome_arquivo


# ── Gráfico 1: Distribuição de Grau ─────────────────────────────────────────

def gerar_distribuicao_grau() -> bool:
    """Histograma da distribuição de grau para as 3 categorias."""
    exibir_secao("VISUALIZAÇÃO 1 — DISTRIBUIÇÃO DE GRAU")
    dados = _carregar_grafos()
    if dados is None:
        return False

    os.makedirs(_OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Distribuição de Grau por Categoria de Review", fontsize=13, fontweight="bold")

    for i, cat in enumerate(_CATEGORIAS):
        g = dados[cat]["graph"]
        graus = [len(vizinhos) for vizinhos in g.values()]

        ax = axes[i]
        ax.hist(graus, bins=40, color=_CORES[cat], edgecolor="none", alpha=0.85)
        ax.set_title(f"{_LABELS[cat]} Reviews", fontsize=11, fontweight="bold")
        ax.set_xlabel("Grau (nº de vizinhos)", fontsize=9)
        ax.set_ylabel("Frequência (nº de palavras)", fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        if graus:
            media = sum(graus) / len(graus)
            ax.axvline(media, color="black", linestyle="--", linewidth=1.2, alpha=0.7)
            ylim = ax.get_ylim()[1]
            ax.text(media * 1.05, ylim * 0.88, f"média={media:.1f}", fontsize=8, color="black")
            log_dados(f"{_LABELS[cat]}: {len(graus)} nós, grau médio={media:.1f}, max={max(graus)}")

    plt.tight_layout()
    _salvar_fig("distribuicao_grau.png")
    log_ok(f"Gráfico salvo em '{_OUTPUT_DIR}/distribuicao_grau.png'")

    _salvar_md("distribuicao_grau.md", """# Visualização 1 — Distribuição de Grau dos Grafos de Coocorrência

![Distribuição de Grau](distribuicao_grau.png)

## O que é este gráfico?

Cada histograma mostra a **distribuição de grau** de um grafo de coocorrência — quantos vizinhos (palavras distintas com que coocorreu) cada palavra possui.

O eixo X representa o **grau do nó** e o eixo Y representa **quantas palavras** possuem aquele grau. A linha tracejada marca o grau médio da rede.

## Tipo de análise

**Análise topológica global** — revela o padrão de conectividade da rede como um todo, sem focar em palavras individuais.

## O que podemos concluir?

- **Pico à esquerda (cauda longa)**: a maioria das palavras é especializada — coocorre com poucos outros termos. Isso é característico de redes de linguagem natural e valida a estrutura dos grafos.
- **Cauda à direita**: as palavras com grau alto são os *hubs semânticos* — os mesmos termos que o PageRank identifica como mais centrais.
- **Comparação entre categorias**: diferenças no grau médio e na forma do histograma revelam se o discurso é concentrado (poucos temas dominam) ou pulverizado (muitos temas distintos aparecem com pouca repetição).
- **BAD vs GOOD**: se BAD tiver grau médio menor, o vocabulário de insatisfação é mais fragmentado e variado; se for maior, há um conjunto fixo de termos de reclamação altamente recorrentes.
""")
    log_ok("Markdown 'distribuicao_grau.md' gerado.")
    return True


# ── Gráfico 2: Comparativo Top 10 ───────────────────────────────────────────

def gerar_comparativo_top10() -> bool:
    """Barras agrupadas comparando o score de PageRank do top 10 de cada categoria."""
    exibir_secao("VISUALIZAÇÃO 2 — COMPARATIVO TOP 10")
    dados = _carregar_grafos()
    if dados is None:
        return False

    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    calc = PageRankCalculator()

    scores_cat = {}
    for cat in _CATEGORIAS:
        scores_cat[cat] = calc.calculate(dados[cat]["graph"], dados[cat]["id_to_word"])

    # Coleta top 10 de cada categoria (sem repetição, preservando ordem de relevância)
    todas_palavras = []
    seen: set = set()
    for cat in _CATEGORIAS:
        for w, _ in calc.get_top_k(scores_cat[cat], k=10):
            if w not in seen:
                todas_palavras.append(w)
                seen.add(w)

    x = list(range(len(todas_palavras)))
    width = 0.27

    fig, ax = plt.subplots(figsize=(max(13, len(todas_palavras)), 6))

    for i, cat in enumerate(_CATEGORIAS):
        vals = [scores_cat[cat].get(w, 0) * 1000 for w in todas_palavras]
        offsets = [xi + (i - 1) * width for xi in x]
        ax.bar(offsets, vals, width=width, label=_LABELS[cat],
               color=_CORES[cat], alpha=0.85, edgecolor="none")

    ax.set_xticks(x)
    ax.set_xticklabels(todas_palavras, rotation=35, ha="right", fontsize=9)
    ax.set_ylabel("PageRank (×10⁻³)", fontsize=9)
    ax.set_title("Comparativo de Relevância — Top 10 Palavras por Categoria (PageRank)",
                 fontsize=12, fontweight="bold")
    ax.legend(title="Categoria", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()

    _salvar_fig("comparativo_top10.png")
    log_ok(f"Gráfico salvo em '{_OUTPUT_DIR}/comparativo_top10.png'")

    _salvar_md("comparativo_top10.md", """# Visualização 2 — Comparativo Top 10 por Categoria (PageRank)

![Comparativo Top 10](comparativo_top10.png)

## O que é este gráfico?

Barras agrupadas mostrando o **score de PageRank (×10⁻³)** das palavras mais centrais de cada categoria de review (BAD / MID / GOOD).

Cada grupo de três barras representa uma palavra — as cores indicam o quanto aquela palavra é central no discurso de cada faixa de avaliação.

## Tipo de análise

**Análise comparativa de centralidade** — mostra simultaneamente a importância relativa de cada palavra nas três categorias, algo impossível de ver em rankings separados.

## O que podemos concluir?

- **Barras altas nas 3 cores**: palavra-âncora do domínio — estrutural, sem carga sentimental (ex: nome do produto, termos logísticos básicos).
- **Barra alta apenas em BAD (vermelha)**: indicador de insatisfação — quando aparece, prediz avaliação negativa.
- **Barra alta apenas em GOOD (verde)**: marcador de satisfação — emerge com força quando o usuário está satisfeito.
- **Assimetria de altura**: quanto maior a diferença de altura entre as barras de uma palavra, maior seu **poder discriminativo** para separar avaliações boas de ruins.
- **Diferença BAD–GOOD em palavras específicas**: a distância vertical entre a barra vermelha e a verde é diretamente proporcional ao potencial daquela palavra como *feature* de um classificador de sentimento.
""")
    log_ok("Markdown 'comparativo_top10.md' gerado.")
    return True


# ── Gráfico 3: Heatmap de Coocorrência ──────────────────────────────────────

def gerar_heatmap_coocorrencia() -> bool:
    """Heatmap das coocorrências entre as top 15 palavras de cada categoria."""
    exibir_secao("VISUALIZAÇÃO 3 — HEATMAP DE COOCORRÊNCIA")
    dados = _carregar_grafos()
    if dados is None:
        return False

    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    calc = PageRankCalculator()

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle("Heatmap de Coocorrência — Top 15 Palavras por Categoria",
                 fontsize=13, fontweight="bold")

    for i, cat in enumerate(_CATEGORIAS):
        g = dados[cat]["graph"]
        id_to_word = dados[cat]["id_to_word"]
        word_to_id = {w: idx for idx, w in enumerate(id_to_word)}

        pr = calc.calculate(g, id_to_word)
        top15 = [w for w, _ in calc.get_top_k(pr, k=15)]

        matrix = np.zeros((15, 15))
        for row_i, w1 in enumerate(top15):
            id1 = str(word_to_id.get(w1, -1))
            if id1 == "-1" or id1 not in g:
                continue
            vizinhos = g[id1]
            for col_j, w2 in enumerate(top15):
                id2 = str(word_to_id.get(w2, -1))
                if id2 in vizinhos:
                    matrix[row_i][col_j] = float(vizinhos[id2])

        ax = axes[i]
        im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(range(15))
        ax.set_yticks(range(15))
        ax.set_xticklabels(top15, rotation=45, ha="right", fontsize=7)
        ax.set_yticklabels(top15, fontsize=7)
        ax.set_title(f"{_LABELS[cat]} Reviews", fontsize=10, fontweight="bold")
        plt.colorbar(im, ax=ax, shrink=0.8, label="Frequência de coocorrência")
        log_dados(f"{_LABELS[cat]}: top 15 = {top15[:5]}...")

    plt.tight_layout()
    _salvar_fig("heatmap_coocorrencia.png")
    log_ok(f"Gráfico salvo em '{_OUTPUT_DIR}/heatmap_coocorrencia.png'")

    _salvar_md("heatmap_coocorrencia.md", """# Visualização 3 — Heatmap de Coocorrência (Top 15 Palavras)

![Heatmap de Coocorrência](heatmap_coocorrencia.png)

## O que é este gráfico?

Uma **matriz de calor** onde linhas e colunas representam as 15 palavras mais centrais de cada categoria (por PageRank). A intensidade da cor em cada célula indica a **frequência de coocorrência** entre dois termos na janela deslizante.

Células escuras (laranja/vermelho) = alta frequência de coocorrência. Células claras (amarelo/branco) = baixa ou nenhuma coocorrência.

## Tipo de análise

**Análise estrutural do núcleo semântico** — revela como os termos mais importantes se relacionam entre si, identificando "combos" linguísticos rígidos.

## O que podemos concluir?

- **Blocos diagonais quentes**: grupos de palavras que formam clusters semânticos — aparecem juntas com alta frequência, formando um padrão de discurso previsível.
- **Células frias fora da diagonal**: apesar de ambas as palavras serem importantes individualmente, elas vivem em contextos diferentes e raramente coocorrem.
- **Linha/coluna inteiramente quente**: aquela palavra coocorre com praticamente todos os outros hubs — é um conector universal do vocabulário.
- **Diferenças entre BAD/MID/GOOD**: revelam se o discurso de insatisfação tem combinações mais rígidas (clusters densos) ou se é mais disperso (matriz mais fria).
- **Assimetria esperada**: a matriz deve ser simétrica em relação à diagonal, pois coocorrência é bidirecional — divergências indicam frequências diferentes em cada direção da janela deslizante.
""")
    log_ok("Markdown 'heatmap_coocorrencia.md' gerado.")
    return True


# ── Gráfico 4: Scatter de Deslocamento ──────────────────────────────────────

def gerar_scatter_deslocamento() -> bool:
    """Scatter plot comparando o ranking PageRank GOOD vs BAD para palavras em comum."""
    exibir_secao("VISUALIZAÇÃO 4 — SCATTER DE DESLOCAMENTO (GOOD vs BAD)")
    dados = _carregar_grafos()
    if dados is None:
        return False

    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    calc = PageRankCalculator()

    pr_good = calc.calculate(dados["good_reviews"]["graph"], dados["good_reviews"]["id_to_word"])
    pr_bad = calc.calculate(dados["bad_reviews"]["graph"], dados["bad_reviews"]["id_to_word"])

    top_good = {w: rank + 1 for rank, (w, _) in enumerate(calc.get_top_k(pr_good, k=50))}
    top_bad = {w: rank + 1 for rank, (w, _) in enumerate(calc.get_top_k(pr_bad, k=50))}

    comuns = list(set(top_good.keys()) & set(top_bad.keys()))
    ranks_good = [top_good[w] for w in comuns]
    ranks_bad = [top_bad[w] for w in comuns]
    deslocamentos = [abs(top_good[w] - top_bad[w]) for w in comuns]

    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(
        ranks_good, ranks_bad,
        c=deslocamentos, cmap="RdYlGn_r",
        s=[60 + d * 8 for d in deslocamentos],
        alpha=0.8, edgecolors="none"
    )
    plt.colorbar(scatter, ax=ax, label="|Δ rank| — Força do deslocamento")

    lim = max(max(ranks_good, default=1), max(ranks_bad, default=1)) + 2
    ax.plot([1, lim], [1, lim], color="gray", linestyle="--", linewidth=1,
            alpha=0.5, label="Sem deslocamento (linha diagonal)")

    # Anota as 8 palavras com maior deslocamento
    top_deslocados = sorted(zip(comuns, deslocamentos), key=lambda x: x[1], reverse=True)[:8]
    for w, _ in top_deslocados:
        ax.annotate(w, (top_good[w], top_bad[w]), fontsize=7.5, ha="left",
                    xytext=(4, 2), textcoords="offset points", color="#333333")

    ax.set_xlabel("Posição no Ranking — GOOD Reviews (1 = mais central)", fontsize=10)
    ax.set_ylabel("Posição no Ranking — BAD Reviews (1 = mais central)", fontsize=10)
    ax.set_title("Deslocamento de Centralidade: GOOD vs BAD (Top 50 compartilhado)",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.invert_xaxis()
    ax.invert_yaxis()
    plt.tight_layout()

    _salvar_fig("scatter_deslocamento.png")
    log_ok(f"Gráfico salvo em '{_OUTPUT_DIR}/scatter_deslocamento.png'")
    log_dados(f"{len(comuns)} palavras em comum entre top-50 de GOOD e BAD")

    _salvar_md("scatter_deslocamento.md", """# Visualização 4 — Scatter de Deslocamento (GOOD vs BAD)

![Scatter de Deslocamento](scatter_deslocamento.png)

## O que é este gráfico?

Um **gráfico de dispersão** onde cada ponto representa uma palavra presente no Top 50 de centralidade (PageRank) tanto de GOOD quanto de BAD Reviews simultaneamente.

- **Eixo X**: posição de ranking na categoria GOOD (1 = mais central, eixo invertido)
- **Eixo Y**: posição de ranking na categoria BAD (1 = mais central, eixo invertido)
- **Cor e tamanho do ponto**: intensidade do deslocamento (|Δ rank| entre as duas categorias)

## Tipo de análise

**Análise de discriminação sentimental** — identifica quais palavras mudam mais de importância conforme o nível de satisfação do usuário.

## O que podemos concluir?

- **Pontos próximos à diagonal cinza**: palavras estruturais do domínio — igualmente centrais em ambas as categorias, sem carga sentimental (ex: nome do produto, termos de entrega).
- **Pontos abaixo da diagonal** (BAD rank melhor que GOOD): palavras que emergem com força nas avaliações negativas — candidatos diretos a indicadores de insatisfação.
- **Pontos acima da diagonal** (GOOD rank melhor que BAD): palavras que emergem com força nas avaliações positivas — marcadores de satisfação.
- **Pontos mais vermelhos e grandes**: máximo poder discriminativo — são os melhores candidatos a *features* em um modelo de classificação de sentimento ou análise de causa-raiz.
- **Rótulos anotados**: as 8 palavras com maior deslocamento são identificadas diretamente no gráfico para análise imediata.
""")
    log_ok("Markdown 'scatter_deslocamento.md' gerado.")
    return True


# ── Gráfico 5: Word Cloud por PageRank ──────────────────────────────────────

def gerar_wordcloud_pagerank() -> bool:
    """Word cloud com tamanho e cor proporcionais ao score de PageRank."""
    exibir_secao("VISUALIZAÇÃO 5 — WORD CLOUD (PAGERANK)")
    dados = _carregar_grafos()
    if dados is None:
        return False

    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    calc = PageRankCalculator()
    rng = random.Random(42)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Word Cloud por Score de PageRank", fontsize=14, fontweight="bold")

    for i, cat in enumerate(_CATEGORIAS):
        pr = calc.calculate(dados[cat]["graph"], dados[cat]["id_to_word"])
        top_words = calc.get_top_k(pr, k=40)

        ax = axes[i]
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_facecolor("#f8f8f8")
        ax.set_title(f"{_LABELS[cat]} Reviews", fontsize=11, fontweight="bold",
                     color=_CORES[cat], pad=8)

        if not top_words:
            continue

        max_score = top_words[0][1]
        min_score = top_words[-1][1]
        score_range = max_score - min_score if max_score != min_score else 1

        base_rgb = mcolors.to_rgb(_CORES[cat])
        placed: list = []

        for word, score in top_words:
            norm = (score - min_score) / score_range
            font_size = 8 + norm * 26

            for _ in range(300):
                x = rng.uniform(0.06, 0.94)
                y = rng.uniform(0.08, 0.92)
                char_w = font_size * 0.013 * len(word)
                char_h = font_size * 0.018

                overlap = any(
                    abs(x - px) < char_w and abs(y - py) < char_h
                    for px, py in placed
                )
                if not overlap:
                    placed.append((x, y))
                    intensity = 0.45 + norm * 0.55
                    color = tuple(min(1.0, c * intensity) for c in base_rgb)
                    weight = "bold" if norm > 0.45 else "normal"
                    ax.text(x, y, word, fontsize=font_size, ha="center", va="center",
                            color=color, fontweight=weight, transform=ax.transAxes,
                            alpha=0.85 + norm * 0.15)
                    break

        log_dados(f"{_LABELS[cat]}: {len(placed)}/{len(top_words)} palavras posicionadas")

    plt.tight_layout()
    _salvar_fig("wordcloud_pagerank.png")
    log_ok(f"Gráfico salvo em '{_OUTPUT_DIR}/wordcloud_pagerank.png'")

    _salvar_md("wordcloud_pagerank.md", """# Visualização 5 — Word Cloud por Score de PageRank

![Word Cloud PageRank](wordcloud_pagerank.png)

## O que é este gráfico?

Uma **nuvem de palavras** onde o **tamanho** e a **intensidade de cor** de cada termo são proporcionais ao seu score de PageRank na rede de coocorrência.

As palavras maiores e mais escuras são as mais centrais no discurso da categoria. As três nuvens permitem comparação visual imediata do vocabulário dominante em avaliações ruins, médias e boas.

## Tipo de análise

**Análise de impacto visual e comunicação executiva** — transforma dados quantitativos (scores de PageRank) em representação visual intuitiva.

## O que podemos concluir?

- **Palavras grandes**: os hubs semânticos do discurso — aparecem em muitos contextos e conectam o vocabulário inteiro (mesmas palavras identificadas pelo PageRank como top rankeadas).
- **Palavras pequenas**: termos especializados que aparecem em contextos específicos mas ainda estão no Top 40 de relevância.
- **Comparação visual entre categorias**: se as três nuvens forem visualmente similares, o vocabulário é predominantemente estrutural; se forem distintas, os usuários mudam radicalmente o que falam conforme o nível de satisfação.
- **Densidade da nuvem**: uma nuvem mais "cheia" (muitas palavras com tamanhos similares) indica vocabulário mais distribuído; uma nuvem com poucas palavras dominantes indica concentração de discurso em poucos termos.
- **Uso executivo**: este é o gráfico mais adequado para apresentações a stakeholders não-técnicos — gerentes e equipes de produto conseguem captar o "DNA linguístico" de cada categoria em segundos.
""")
    log_ok("Markdown 'wordcloud_pagerank.md' gerado.")
    return True


# ── Runner de todas as visualizações ────────────────────────────────────────

def run_todas_visualizacoes() -> None:
    """Executa os 5 gráficos em sequência."""
    fns = [
        ("Distribuição de Grau",    gerar_distribuicao_grau),
        ("Comparativo Top 10",      gerar_comparativo_top10),
        ("Heatmap de Coocorrência", gerar_heatmap_coocorrencia),
        ("Scatter de Deslocamento", gerar_scatter_deslocamento),
        ("Word Cloud (PageRank)",   gerar_wordcloud_pagerank),
    ]
    for nome, fn in fns:
        ok = fn()
        if not ok:
            log_aviso(f"'{nome}' não pôde ser gerado (grafos ausentes?).")
