import os
import json
import random
import shutil
import matplotlib.pyplot as plt
import networkx as nx

from src.preprocessing.processor_manager import ProcessManager
from src.graph_construction.graph_builder import build_graphs_from_categories
from src.analysis.pagerank import PageRankCalculator


def pipeline_grafos_e_visualizacao(input_amostra_dir, processed_dir, output_opcao_dir, titulo_md, subtitulo_md):
    """
    Função coringa que roda o pré-processamento, constrói os grafos,
    calcula o PageRank local, filtra e gera os plots PNG (Grafo + Barras de Relevância)
    e exporta um relatório executivo em Markdown com imagens embutidas.
    """
    # --- RESET DO DIRETÓRIO DE OUTPUT ---
    if os.path.exists(output_opcao_dir):
        print(f"[*] Limpando artefatos antigos em '{output_opcao_dir}'...")
        shutil.rmtree(output_opcao_dir)

    os.makedirs(output_opcao_dir, exist_ok=True)

    print("[+] Rodando pré-processamento (Sliding Window)...")
    processor = ProcessManager(input_dir=input_amostra_dir, output_dir=processed_dir)
    processor.process_all_tiers()

    print("\n--- FASE 4: CONSTRUÇÃO DOS GRAFOS ---")
    categorias = ["bad_reviews", "mid_reviews", "good_reviews"]
    build_graphs_from_categories(processed_dir, categorias)

    print("\n[+] Gerando visualizações geométricas e estatísticas dos grafos...")
    calc_pr = PageRankCalculator()

    # Inicializa o relatório Markdown
    markdown_lines = [
        f"# {titulo_md}",
        f"{subtitulo_md}",
        "",
        "---",
        ""
    ]

    for cat in categorias:
        graph_path = f"data/graphs/{cat}_graph.json"
        if not os.path.exists(graph_path):
            continue

        with open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        graph_dict = graph_data["grafo"]["graph"]
        id_to_word = graph_data["grafo"]["id_to_word"]

        # 1. CÁLCULO DE RELEVÂNCIA (PAGERANK)
        scores_pr = calc_pr.calculate(graph_dict, id_to_word)
        top_5 = calc_pr.get_top_k(scores_pr, k=5)
        top_5_words = [word for word, _ in top_5]

        # Calcular a soma total do PageRank para converter em porcentagem do ecossistema
        total_pr_score = sum(scores_pr.values()) if scores_pr.values() else 1

        # 2. GERAÇÃO DO GRÁFICO DE BARRAS HORIZONTAIS (DISTRIBUIÇÃO DE RELEVÂNCIA)
        plt.figure(figsize=(7, 4))

        # Inverte a ordem para a palavra mais relevante ficar no topo do gráfico de barras horizontais
        palavras_barras = [word for word, _ in top_5][::-1]
        porcentagens_barras = [(score / total_pr_score) * 100 for _, score in top_5][::-1]

        # Desenha as barras com uma cor limpa e moderna
        bars = plt.barh(palavras_barras, porcentagens_barras, color='#1F78B4', edgecolor='none', height=0.6)

        # Adiciona o valor de porcentagem impresso na ponta de cada barra
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.2, bar.get_y() + bar.get_height() / 2, f'{width:.2f}%',
                     va='center', ha='left', fontsize=9, fontweight='bold', color='#333333')

        plt.title(f"Top 5 Palavras por Importância Relativa - {cat.upper()}", fontsize=11, fontweight="bold", pad=15)
        plt.xlabel("Participação de Influência no Grafo (%)", fontsize=9)
        plt.xlim(0, max(porcentagens_barras) * 1.2)  # Dá um respiro para o texto não cortar
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.tight_layout()

        img_bar_filename = f"{cat}_distribuicao_barras.png"
        img_bar_path = os.path.join(output_opcao_dir, img_bar_filename)
        plt.savefig(img_bar_path, format="PNG", dpi=130)
        plt.close()

        # 3. FILTRAGEM E MONTAGEM DO GRAFO GEOMÉTRICO (REDE)
        todas_palavras_validas = set()
        arestas_validas = []

        for u, neighbors in graph_dict.items():
            u_word = id_to_word[int(u)]
            for v, w in neighbors.items():
                v_word = id_to_word[int(v)]
                if int(w) > 1:
                    arestas_validas.append((u_word, v_word, int(w)))
                    todas_palavras_validas.add(u_word)
                    todas_palavras_validas.add(v_word)

        palavras_secundarias = list(todas_palavras_validas - set(top_5_words))
        qtd_amostrar = max(1, int(len(palavras_secundarias) * 0.20))
        secundarias_amostradas = random.sample(palavras_secundarias, min(len(palavras_secundarias), qtd_amostrar))

        palavras_permitidas = set(top_5_words).union(secundarias_amostradas)

        G = nx.Graph()
        for u_word, v_word, w in arestas_validas:
            if u_word in palavras_permitidas and v_word in palavras_permitidas:
                G.add_edge(u_word, v_word, weight=w)

        G.remove_nodes_from(list(nx.isolates(G)))

        # Plot da Rede
        plt.figure(figsize=(11, 9))
        plt.title(f"Grafo de Coocorrência Semântica (Enxuto) - {cat.upper()}", fontsize=13, fontweight="bold", pad=10)

        pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
        node_colors = ['#FF4500' if node in top_5_words else '#A6CEE3' for node in G.nodes()]
        node_sizes = [950 if node in top_5_words else 220 for node in G.nodes()]

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.85)
        nx.draw_networkx_edges(G, pos, alpha=0.12, edge_color="gray")

        labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(
            G, pos, labels=labels,
            font_size=9,
            font_family="sans-serif",
            font_weight="bold",
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.75, pad=1.5)
        )

        plt.axis('off')
        plt.tight_layout()

        img_graph_filename = f"{cat}_vis_rede.png"
        img_graph_path = os.path.join(output_opcao_dir, img_graph_filename)
        plt.savefig(img_graph_path, format="PNG", dpi=130)
        plt.close()

        # 4. ALIMENTAÇÃO DINÂMICA DO MARKDOWN (EMBUTINDO AS IMAGENS COM SINTAXE MD)
        markdown_lines.append(f"## 📈 Categoria Estrutural: `{cat.upper()}`")
        markdown_lines.append(f"* **Principais Hubs (Top PageRank):** {', '.join(top_5_words)}")
        markdown_lines.append("")
        markdown_lines.append("#### Análise Estatística e Topologia da Rede:")
        # Usar caminhos relativos diretos (apenas o nome do arquivo) faz o MD renderizar perfeitamente local
        markdown_lines.append(f"<table>")
        markdown_lines.append(f"  <tr>")
        markdown_lines.append(f"    <td><img src='{img_bar_filename}' width='450' alt='Distribuição'/></td>")
        markdown_lines.append(f"    <td><img src='{img_graph_filename}' width='550' alt='Rede Coocorrência'/></td>")
        markdown_lines.append(f"  </tr>")
        markdown_lines.append(f"</table>")
        markdown_lines.append("")
        markdown_lines.append("---")
        markdown_lines.append("")

    # Gravação do relatório consolidado
    md_path = os.path.join(output_opcao_dir, "resultado_execucao.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))

    gerar_analise_diferencial(processed_dir, output_opcao_dir)

    print(f"\n[SUCESSO] Pipeline concluída! Relatório Markdown e gráficos gerados em '{output_opcao_dir}/'!")


def gerar_analise_diferencial(processed_dir, output_opcao_dir):
    """
    Analisa os grafos das três categorias para identificar interseções,
    palavras exclusivas e o deslocamento de importância (PageRank) de termos comuns.
    Gera um relatório comparativo em Markdown.
    """
    print("[+] Computando análise diferencial entre as categorias...")

    categorias = ["bad_reviews", "mid_reviews", "good_reviews"]
    dados_cats = {}
    calc_pr = PageRankCalculator()

    # Carrega os dados e calcula o PageRank completo de cada uma
    for cat in categorias:
        graph_path = f"data/graphs/{cat}_graph.json"
        if not os.path.exists(graph_path):
            return

        with open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        graph_dict = graph_data["grafo"]["graph"]
        id_to_word = graph_data["grafo"]["id_to_word"]

        # Obter dicionário de scores: { "palavra": score }
        scores_pr = calc_pr.calculate(graph_dict, id_to_word)

        # Guardamos o top 30 para fazer cruzamentos relevantes
        top_30_lista = calc_pr.get_top_k(scores_pr, k=30)
        top_30_words = [word for word, _ in top_30_lista]

        # Mapeamento de rank (posição) para identificar deslocamentos
        word_to_rank = {word: idx + 1 for idx, (word, _) in enumerate(top_30_lista)}

        # --- AQUI ESTAVA O BUG: Removido o .values() ---
        dados_cats[cat] = {
            "todas": set(id_to_word),  # <--- Mudado de set(id_to_word.values()) para set(id_to_word)
            "top_30": set(top_30_words),
            "ranks": word_to_rank,
            "scores": scores_pr
        }

    # --- PROCESSAMENTO DOS INSIGHTS ---
    good_top = dados_cats["good_reviews"]["top_30"]
    mid_top = dados_cats["mid_reviews"]["top_30"]
    bad_top = dados_cats["bad_reviews"]["top_30"]

    # 1. Palavras que são Hubs Globais (estão no Top 30 de TODAS)
    hubs_globais = good_top.intersection(mid_top).intersection(bad_top)

    # 2. Palavras exclusivas do Top de cada extremo (Good vs Bad)
    exclusivas_good = good_top - bad_top - mid_top
    exclusivas_bad = bad_top - good_top - mid_top

    # 3. Deslocamento de Rank (Palavras que flutuam de importância)
    # Procuramos palavras que estão no topo de Good e Bad, mas em posições muito diferentes
    deslocamentos = []
    palavras_comuns_extremos = good_top.intersection(bad_top)

    for word in palavras_comuns_extremos:
        rank_good = dados_cats["good_reviews"]["ranks"].get(word, 99)
        rank_bad = dados_cats["bad_reviews"]["ranks"].get(word, 99)
        diff = abs(rank_good - rank_bad)
        if diff >= 3:  # Relevante se mudou pelo menos 3 posições de importância
            deslocamentos.append((word, rank_good, rank_bad, diff))

    # Ordena pelo tamanho do deslocamento
    deslocamentos.sort(key=lambda x: x[3], reverse=True)

    # --- MONTAGEM DO MARKDOWN COMPARATIVO ---
    md_lines = [
        "# 📑 Relatório de Análise Diferencial e Contraste Semântico",
        "Este relatório apresenta uma análise comparativa profunda sobre a topologia e a semântica dos grafos de coocorrência das categorias **GOOD**, **MID** e **BAD** reviews. O objetivo é mapear cientificamente como a estrutura do discurso e a importância de determinados conceitos mudam conforme o nível de satisfação do usuário.",
        "",
        "---",
        "",
        "## 1. Hubs Vocabulares Globais (Interseção Semântica)",
        "### O que significa?",
        "Estes termos pertencem à interseção estrita do **Top 30 de PageRank** de todas as três categorias simultaneamente. Significa que, independentemente da nota da review, a centralidade estrutural dessas palavras na rede de coocorrência permanece massiva.",
        "",
        "### Impacto e Interpretação nas Reviews:",
        "Por estarem no núcleo de todas as vertentes emocionais, essas palavras representam a **base estrutural e o domínio do dataset** (ex: substantivos essenciais do produto analisado ou verbos de ação mandatórios). Elas funcionam como *âncoras de contexto*: não carregam polaridade sentimental por si só, mas servem como a espinha dorsal sobre a qual as opiniões (positivas ou negativas) são construídas. Identificá-las é crucial para entender qual é o foco temático comum e inegociável de atenção de todos os usuários.",
        "",
        f"* **Palavras Compartilhadas (Hubs de Domínio):** {', '.join(hubs_globais) if hubs_globais else 'Nenhuma'}",
        "",
        "---",
        "",
        "## 2. Assinaturas Exclusivas de Sentimento (Diferenças Topológicas)",
        "### O que significa?",
        "São palavras que alcançaram relevância crítica (Top 30) **exclusivamente** em uma determinada categoria de review, desaparecendo do topo ou sequer existindo nas vertentes opostas.",
        "",
        "### Impacto e Interpretação nas Reviews:",
        "Essas palavras são as verdadeiras **assinaturas emocionais** do comportamento do usuário. Elas isolam os fatores puros que geram extrema satisfação ou profunda frustração: ",
        "",
        "* As exclusivas em **GOOD** mapeiam os diferenciais competitivos e os maiores acertos da experiência (recursos que encantam e fidelizam o usuário).",
        "* As exclusivas em **BAD** funcionam como um diagnóstico imediato de falhas críticas, bugs de performance, quebras de expectativa ou pontos de fricção severos na jornada.",
        "",
        "Isolar esses termos permite à engenharia entender exatamente o que é o 'fator de valor' e o que é o 'fator de rejeição' sem a interferência de ruídos ou termos neutros.",
        "",
        "### Exclusivas de Críticas Positivas (`GOOD`):",
        f"* {', '.join(exclusivas_good) if exclusivas_good else 'Nenhuma'}",
        "",
        "### Exclusivas de Críticas Negativas (`BAD`):",
        f"* {', '.join(exclusivas_bad) if exclusivas_bad else 'Nenhuma'}",
        "",
        "---",
        "",
        "## 3. Deslocamento de Centralidade (Flutuação de Importância via PageRank)",
        "### O que significa?",
        "Esta métrica monitora termos voláteis: palavras que conseguiram entrar no Top 30 tanto de críticas positivas quanto negativas, mas sofreram uma variação drástica em suas posições de ranking (força de centralidade) com uma variação absoluta (|Δ|) de pelo menos 3 posições.",
        "",
        "### Impacto e Interpretação nas Reviews:",
        "Este fenômeno revela o **deslocamento de foco de atenção** guiado pela emoção. Quando um termo apresenta um PageRank muito mais alto nas críticas negativas do que nas positivas, isso indica que, quando o recurso associado àquela palavra falha, ele monopoliza o discurso do usuário e se torna o principal assunto gerador de insatisfação (ex: um sistema que passa despercebido quando funciona perfeitamente, mas vira o centro das atenções se quebrar). ",
        "",
        "A tabela abaixo ordena as palavras pela maior força de deslocamento, evidenciando quais conceitos sofrem a maior metamorfose de relevância dentro do ecossistema estudado:",
        ""
    ]

    if deslocamentos:
        md_lines.append("| Palavra | Posição em GOOD | Posição em BAD | Força do Deslocamento |")
        md_lines.append("| :--- | :---: | :---: | :---: |")
        for word, r_good, r_bad, diff in deslocamentos[:8]:  # Pega as 8 variações mais brutas
            md_lines.append(f"| **{word}** | #{r_good} | #{r_bad} | Δ {diff} posições |")
    else:
        md_lines.append("*Nenhuma palavra apresentou variação drástica de posição entre os extremos.*")

    # Escrita do arquivo
    output_path = os.path.join(output_opcao_dir, "analise_diferencial.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"[SUCESSO] Relatório diferencial exportado em '{output_path}'!")