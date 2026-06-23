import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.graph_construction.graph_builder import GraphBuilder
from src.interface.console import exibir_secao, log_info, log_ok, log_aviso


def run_dfs_analysis():
    """
    Executa a análise de componentes conexos (DFS) sobre os grafos já construídos
    e gera um relatório Markdown comparando a fragmentação do discurso entre categorias.

    Diferença conceitual em relação ao BFS:
    - BFS explora a vizinhança de UMA palavra específica, camada por camada
      (responde: "o que está relacionado a essa palavra?")
    - DFS identifica TODOS os componentes conexos do grafo inteiro
      (responde: "esse grafo é um bloco só, ou existem ilhas isoladas de vocabulário?")
    """
    graphs_dir = "data/graphs"
    reports_dir = "outputs/reports"
    os.makedirs(reports_dir, exist_ok=True)

    categories = ["bad_reviews", "mid_reviews", "good_reviews"]

    markdown_lines = [
        "# Relatório de Fragmentação Semântica via Busca em Profundidade (DFS)",
        "",
        "Este relatório utiliza o algoritmo de busca em profundidade para identificar "
        "os **componentes conexos** de cada grafo de coocorrência, ou seja, blocos de "
        "palavras que estão conectados entre si, mas isolados do restante do vocabulário.",
        "",
        "Diferente do BFS (que explora a vizinhança de uma palavra específica), o DFS aqui "
        "responde a uma pergunta estrutural sobre o grafo como um todo: **o discurso da "
        "categoria é unificado em um só bloco temático, ou se fragmenta em vários subtemas "
        "desconectados?**",
        ""
    ]

    exibir_secao("ANÁLISE DE FRAGMENTAÇÃO (DFS)")

    for cat in categories:
        graph_path = os.path.join(graphs_dir, f"{cat}_graph.json")
        if not os.path.exists(graph_path):
            log_aviso(f"Grafo de {cat} não encontrado. Pulando...")
            continue

        with open(graph_path, "r", encoding="utf-8") as f:
            dados_json = json.load(f)

        # IMPORTANTE: o JSON salva todas as chaves de dicionário como string.
        # O GraphBuilder espera ids inteiros (eles funcionam como índice de lista
        # em id_to_word), então convertemos de volta aqui antes de usar.
        graph_bruto = dados_json["grafo"]["graph"]
        builder = GraphBuilder()
        builder.graph = {
            int(vertice_id): {int(vizinho_id): peso for vizinho_id, peso in vizinhos.items()}
            for vertice_id, vizinhos in graph_bruto.items()
        }
        builder.id_to_word = dados_json["grafo"]["id_to_word"]
        builder.word_to_id = dados_json["grafo"]["word_to_id"]

        # Usa o método DFS que já existe na classe (componentes_conectados)
        componentes = builder.componentes_conectados()
        componentes_ordenados = sorted(componentes, key=len, reverse=True)

        total_vertices = len(builder.id_to_word)
        maior_componente = componentes_ordenados[0] if componentes_ordenados else []
        proporcao_giant = (len(maior_componente) / total_vertices * 100) if total_vertices > 0 else 0
        componentes_isolados = [c for c in componentes_ordenados if len(c) == 1]
        componentes_pequenos = [c for c in componentes_ordenados if 2 <= len(c) <= 5]

        log_info(f"{cat}: {len(componentes_ordenados)} componentes encontrados "
                 f"(maior cobre {proporcao_giant:.1f}% do vocabulário)")

        markdown_lines.append(f"## 📊 Categoria: {cat.upper()}")
        markdown_lines.append("")
        markdown_lines.append(f"* **Total de componentes conexos:** {len(componentes_ordenados)}")
        markdown_lines.append(f"* **Tamanho do maior componente:** {len(maior_componente)} palavras "
                               f"({proporcao_giant:.1f}% do vocabulário total)")
        markdown_lines.append(f"* **Palavras totalmente isoladas (sem nenhuma coocorrência válida):** "
                               f"{len(componentes_isolados)}")
        markdown_lines.append(f"* **Pequenos grupos isolados (2 a 5 palavras):** {len(componentes_pequenos)}")
        markdown_lines.append("")

        # Mostra uma amostra dos menores componentes, pra ilustrar o que ficou "fora" do bloco principal
        if componentes_pequenos:
            markdown_lines.append("**Exemplos de pequenos grupos desconectados do discurso principal:**")
            for comp in componentes_pequenos[:5]:
                markdown_lines.append(f"  - `{', '.join(comp)}`")
            markdown_lines.append("")

        markdown_lines.append("---")
        markdown_lines.append("")

    # Interpretação final comparando as 3 categorias
    markdown_lines.append("## Interpretação")
    markdown_lines.append(
        "Categorias com um componente gigante cobrindo uma fração maior do vocabulário indicam "
        "um discurso mais **coeso e centralizado**, a maioria das palavras está, direta ou "
        "indiretamente, conectada ao mesmo núcleo temático. Já categorias com mais componentes "
        "pequenos e palavras isoladas sugerem um discurso mais **disperso**, com menções pontuais "
        "a assuntos que não se repetem o suficiente para se conectar ao restante do vocabulário."
    )
    markdown_lines.append("")

    report_path = os.path.join(reports_dir, "dfs_components.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))

    log_ok(f"Relatório de componentes conexos (DFS) salvo em: '{report_path}'")


if __name__ == "__main__":
    run_dfs_analysis()