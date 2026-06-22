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

    print(f"\n[SUCESSO] Pipeline concluída! Relatório Markdown e gráficos gerados em '{output_opcao_dir}/'!")