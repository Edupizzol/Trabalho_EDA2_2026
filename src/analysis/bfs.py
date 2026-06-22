import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.graph_construction.graph_builder import GraphBuilder
from src.interface.console import exibir_secao, log_info, log_ok, log_aviso, log_dados


def executar_bfs_contextual(builder, palavra_raiz, max_camadas=2):
    """
    Executa uma BFS modificada para agrupar vizinhos por nível de distância semântica.
    """
    if palavra_raiz not in builder.word_to_id:
        return {}

    start_id = builder.word_to_id[palavra_raiz]
    visitados = {start_id}
    # Fila armazena tuplas: (id_nodo, camada_atual)
    fila = [(start_id, 0)]

    contexto_por_camada = {i: [] for i in range(1, max_camadas + 1)}

    while fila:
        atual_id, camada = fila.pop(0)

        if camada >= max_camadas:
            continue

        # Explora os vizinhos do nodo atual
        vizinhos = builder.graph.get(str(atual_id), builder.graph.get(atual_id, {}))

        # Ordena os vizinhos pelo peso da aresta (frequência) para pegar os contextos mais fortes primeiro
        vizinhos_ordenados = sorted(vizinhos.items(), key=lambda item: item[1], reverse=True)

        for vizinho_str, peso in vizinhos_ordenados:
            vizinho_id = int(vizinho_str)
            if vizinho_id not in visitados:
                visitados.add(vizinho_id)
                proxima_camada = camada + 1

                palavra_vizinha = builder.id_to_word[vizinho_id]
                contexto_por_camada[proxima_camada].append((palavra_vizinha, int(peso)))

                fila.append((vizinho_id, proxima_camada))

    return contexto_por_camada


def run_bfs_analysis():
    graphs_dir = "data/graphs"
    reports_dir = "outputs/reports"
    os.makedirs(reports_dir, exist_ok=True)

    categories = ["bad_reviews", "mid_reviews", "good_reviews"]

    # Define as top palavras sementes que o seu PageRank localizou para cada cenário
    palavras_chave = {
        "bad_reviews": ["produto", "dia", "americana", "compra", "uso"],
        "mid_reviews": ["produto", "entrega", "prazo", "preço", "aparelho"],
        "good_reviews": ["produto", "qualidade", "excelente", "prazo", "entrega"]
    }

    markdown_lines = [
        "# Relatório de Vizinhança Semântica via Busca em Largura (BFS)",
        "",
        "Este relatório utiliza o algoritmo de busca em largura a partir das palavras-âncora do PageRank ",
        "para rastrear o contexto de avaliação dos usuários em 1 e 2 saltos de distância.",
        ""
    ]

    exibir_secao("ANÁLISE DE VIZINHANÇA SEMÂNTICA (BFS)")

    for cat in categories:
        graph_path = os.path.join(graphs_dir, f"{cat}_graph.json")
        if not os.path.exists(graph_path):
            log_aviso(f"Grafo de {cat} não encontrado. Pulando...")
            continue

        with open(graph_path, "r", encoding="utf-8") as f:
            dados_json = json.load(f)

        # Reconstrói a estrutura usando a sua própria classe GraphBuilder
        builder = GraphBuilder()
        builder.graph = dados_json["grafo"]["graph"]
        builder.id_to_word = dados_json["grafo"]["id_to_word"]
        builder.word_to_id = dados_json["grafo"]["word_to_id"]

        markdown_lines.append(f"## 📊 Categoria: {cat.upper()}")
        markdown_lines.append("")

        log_info(f"Analisando adjacências para a categoria: {cat}...")

        for raiz in palavras_chave[cat]:
            res_camadas = executar_bfs_contextual(builder, raiz, max_camadas=2)
            if not res_camadas:
                continue

            markdown_lines.append(f"### 🔍 Palavra-Raiz: `{raiz}`")

            # Camada 1: Conexões Diretas
            c1_text = ", ".join([f"{p} ({w})" for p, w in res_camadas[1][:8]]) or "Nenhuma"
            markdown_lines.append(f"* **Conexões Diretas (Distância 1):** {c1_text}")

            # Camada 2: Contexto Estendido
            c2_text = ", ".join([p for p, _ in res_camadas[2][:10]]) or "Nenhuma"
            markdown_lines.append(f"* **Contexto Estendido (Distância 2):** {c2_text}")
            markdown_lines.append("")

    # Salva o relatório final
    report_path = os.path.join(reports_dir, "bfs_semantic_context.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))

    log_ok(f"Relatório semântico da BFS salvo em: '{report_path}'")


if __name__ == "__main__":
    run_bfs_analysis()