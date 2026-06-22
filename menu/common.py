import os
import json
import random
import shutil  # Importado para fazer a limpeza completa do diretório
import matplotlib.pyplot as plt
import networkx as nx

from src.preprocessing.processor_manager import ProcessManager
from src.graph_construction.graph_builder import build_graphs_from_categories
from src.analysis.pagerank import PageRankCalculator


def pipeline_grafos_e_visualizacao(input_amostra_dir, processed_dir, output_opcao_dir, titulo_md, subtitulo_md):
    """
    Função coringa que roda o pré-processamento, constrói os grafos,
    calcula o PageRank local, filtra e gera os plots PNG espalhados e relatórios MD.
    Garante que o diretório de output esteja completamente limpo a cada execução.
    """
    # --- RESET DO DIRETÓRIO DE OUTPUT ---
    if os.path.exists(output_opcao_dir):
        print(f"[*] Limpando artefatos antigos em '{output_opcao_dir}'...")
        shutil.rmtree(output_opcao_dir)

    # Cria a pasta do zero, garantindo um ambiente limpo para os novos arquivos
    os.makedirs(output_opcao_dir, exist_ok=True)

    print("[+] Rodando pré-processamento (Sliding Window)...")
    processor = ProcessManager(input_dir=input_amostra_dir, output_dir=processed_dir)
    processor.process_all_tiers()

    print("\n--- FASE 4: CONSTRUÇÃO DOS GRAFOS ---")
    categorias = ["bad_reviews", "mid_reviews", "good_reviews"]
    build_graphs_from_categories(processed_dir, categorias)

    print("\n[+] Gerando visualizações geométricas enxutas dos grafos...")
    calc_pr = PageRankCalculator()

    markdown_lines = [
        f"# {titulo_md}",
        f"{subtitulo_md}",
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

        # Calcula o PageRank da amostragem corrente
        scores_pr = calc_pr.calculate(graph_dict, id_to_word)
        top_5 = calc_pr.get_top_k(scores_pr, k=5)
        top_5_words = [word for word, _ in top_5]

        # Separa as arestas estruturais válidas (peso > 1)
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

        # Filtro de 20% das palavras não prioritárias
        palavras_secundarias = list(todas_palavras_validas - set(top_5_words))
        qtd_amostrar = max(1, int(len(palavras_secundarias) * 0.20))
        secundarias_amostradas = random.sample(palavras_secundarias, min(len(palavras_secundarias), qtd_amostrar))

        palavras_permitidas = set(top_5_words).union(secundarias_amostradas)

        # Monta a estrutura visual limpa
        G = nx.Graph()
        for u_word, v_word, w in arestas_validas:
            if u_word in palavras_permitidas and v_word in palavras_permitidas:
                G.add_edge(u_word, v_word, weight=w)

        G.remove_nodes_from(list(nx.isolates(G)))

        # Plot Otimizado
        plt.figure(figsize=(12, 10))
        plt.title(f"Grafo de Coocorrência Semântica (Enxuto) - {cat.upper()}", fontsize=14, fontweight="bold")

        pos = nx.spring_layout(G, k=1.5, iterations=100, seed=42)
        node_colors = ['#FF4500' if node in top_5_words else '#1F78B4' for node in G.nodes()]
        node_sizes = [900 if node in top_5_words else 250 for node in G.nodes()]

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.85)
        nx.draw_networkx_edges(G, pos, alpha=0.15, edge_color="gray")

        labels = {node: node for node in G.nodes()}
        nx.draw_networkx_labels(
            G, pos, labels=labels,
            font_size=9,
            font_family="sans-serif",
            font_weight="bold",
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=2)
        )

        plt.axis('off')
        plt.tight_layout()

        img_filename = f"{cat}_vis.png"
        img_path = os.path.join(output_opcao_dir, img_filename)
        plt.savefig(img_path, format="PNG", dpi=150)
        plt.close()

        markdown_lines.append(f"## 📈 Categoria: {cat}")
        markdown_lines.append(f"* **Palavras-Chave Identificadas (Top PageRank):** {', '.join(top_5_words)}")
        markdown_lines.append(f"* Grafos visuais exportados em: `{img_path}`")
        markdown_lines.append("")

    md_path = os.path.join(output_opcao_dir, "resultado_execucao.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))

    print(f"\n[SUCESSO] Artefatos visuais e MD criados com sucesso em '{output_opcao_dir}/'!")