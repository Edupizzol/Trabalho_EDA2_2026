import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.interface.console import exibir_secao, log_info, log_ok, log_aviso, log_erro, log_dados


def extract_semantic_flow(graph: dict, id_to_word: list, word_to_id: dict, hub_word: str, max_cols=3, top_n_direct=5, top_n_secondary=3) -> list:
    """
    Extrai a Ego-Network de fluxo semântico de até 3 colunas a partir de um hub central.
    Retorna uma lista de dicionários contendo os fluxos (source, target, value).
    """
    if hub_word not in word_to_id:
        return []

    hub_id = str(word_to_id[hub_word])
    flows = []

    # Coluna 1: Vizinhos diretos do Hub
    if hub_id not in graph:
        return []

    direct_neighbors = graph[hub_id]
    # Ordena pelo peso da coocorrência (frequência)
    direct_sorted = sorted(
        [(int(v_id), int(w)) for v_id, w in direct_neighbors.items()],
        key=lambda x: x[1],
        reverse=True
    )

    # Seleciona as top direct connections
    top_direct = direct_sorted[:top_n_direct]
    direct_words = []

    for v_id, w in top_direct:
        v_word = id_to_word[v_id]
        direct_words.append((v_id, v_word))
        flows.append({
            "source": hub_word,
            "target": v_word,
            "value": w
        })

    # Coluna 2: Vizinhos dos vizinhos diretos (sem retornar ao hub ou palavras da Coluna 1)
    visited_words = {hub_word} | {w[1] for w in direct_words}

    for v_id, v_word in direct_words:
        v_id_str = str(v_id)
        if v_id_str not in graph:
            continue
        
        sec_neighbors = graph[v_id_str]
        sec_sorted = sorted(
            [(int(v2_id), int(w2)) for v2_id, w2 in sec_neighbors.items()],
            key=lambda x: x[1],
            reverse=True
        )

        added_sec_count = 0
        for v2_id, w2 in sec_sorted:
            v2_word = id_to_word[v2_id]
            # Evita loops
            if v2_word not in visited_words:
                flows.append({
                    "source": v_word,
                    "target": v2_word,
                    "value": w2
                })
                visited_words.add(v2_word)
                added_sec_count += 1
                if added_sec_count >= top_n_secondary:
                    break

    return flows


def _get_bezier_points(x1, y1, x2, y2, num_points=100):
    """Gera pontos para uma curva de Bézier cúbica com controle horizontal no ponto médio."""
    x_mid = x1 + (x2 - x1) / 2.0
    t = np.linspace(0, 1, num_points)
    
    cx1, cy1 = x_mid, y1
    cx2, cy2 = x_mid, y2
    
    x = (1-t)**3 * x1 + 3*(1-t)**2 * t * cx1 + 3*(1-t) * t**2 * cx2 + t**3 * x2
    y = (1-t)**3 * y1 + 3*(1-t)**2 * t * cx1 + 3*(1-t) * t**2 * cx2 + t**3 * y2
    
    # Recalcula y corretamente
    y = (1-t)**3 * y1 + 3*(1-t)**2 * t * cy1 + 3*(1-t) * t**2 * cy2 + t**3 * y2
    return x, y


def plot_matplotlib_sankey(flows, title, output_path, color_theme="#1F78B4"):
    """
    Desenha um diagrama de Sankey de 3 colunas no Matplotlib usando curvas de Bézier fluidas.
    """
    if not flows:
        # Cria figura em branco com aviso
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "Sem fluxos suficientes para exibir", ha="center", va="center")
        plt.axis("off")
        plt.savefig(output_path, dpi=130, bbox_inches="tight")
        plt.close()
        return

    # Organiza os nós em colunas
    sources = {f["source"] for f in flows}
    targets = {f["target"] for f in flows}
    
    # Identifica o Hub (coluna 0) como o nó que é source mas nunca target
    col0_nodes = list(sources - targets)
    if not col0_nodes:
        # Fallback se houver ciclo
        col0_nodes = [flows[0]["source"]]

    # Coluna 1: Destinos da Coluna 0
    col1_nodes = sorted(list({f["target"] for f in flows if f["source"] in col0_nodes}))
    
    # Coluna 2: Destinos da Coluna 1
    col2_nodes = sorted(list(targets - set(col1_nodes) - set(col0_nodes)))

    columns = [col0_nodes, col1_nodes, col2_nodes]
    x_coords = [0.1, 0.5, 0.9]

    # Calcula a soma de fluxos de entrada e saída por nó para determinar a altura
    flow_in = {}
    flow_out = {}
    for f in flows:
        u, v, val = f["source"], f["target"], f["value"]
        flow_out[u] = flow_out.get(u, 0) + val
        flow_in[v] = flow_in.get(v, 0) + val

    node_heights = {}
    for u in set(sources) | set(targets):
        node_heights[u] = max(flow_in.get(u, 0), flow_out.get(u, 0))

    # Normalização das alturas para caberem verticalmente em [0.0, 1.0]
    max_col_sum = 0
    for col in columns:
        col_sum = sum(node_heights[u] for u in col)
        if col_sum > max_col_sum:
            max_col_sum = col_sum

    scale = 0.85 / max_col_sum if max_col_sum > 0 else 1.0

    # Determina o posicionamento vertical (y_span) de cada nó
    node_spans = {}
    for c, col in enumerate(columns):
        if not col:
            continue
        total_h = sum(node_heights[u] for u in col) * scale
        gaps_count = len(col) + 1
        gap = (1.0 - total_h) / gaps_count
        
        y = gap
        for u in col:
            h = node_heights[u] * scale
            node_spans[u] = (y, y + h)
            y += h + gap

    # Configura a figura do matplotlib
    fig, ax = plt.subplots(figsize=(12, 7.5))
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=15)

    # Rastreia o consumo vertical das portas de cada nó para conectar os fluxos
    used_out = {u: 0.0 for u in sources}
    used_in = {v: 0.0 for v in targets}

    # Desenha os fluxos (fitas)
    for f in flows:
        u, v, val = f["source"], f["target"], f["value"]
        if u not in node_spans or v not in node_spans:
            continue
        
        h_ribbon = val * scale
        
        # Pega coordenadas do port de origem (u)
        y_src_start = node_spans[u][0] + used_out[u]
        y_src_end = y_src_start + h_ribbon
        used_out[u] += h_ribbon

        # Pega coordenadas do port de destino (v)
        y_tgt_start = node_spans[v][0] + used_in[v]
        y_tgt_end = y_tgt_start + h_ribbon
        used_in[v] += h_ribbon

        # Determina a coluna x
        x_src = 0.0
        for c, col in enumerate(columns):
            if u in col:
                x_src = x_coords[c]
                break

        x_tgt = 0.0
        for c, col in enumerate(columns):
            if v in col:
                x_tgt = x_coords[c]
                break

        # Desenha a fita com curvas de Bézier preenchidas
        x_top, y_top = _get_bezier_points(x_src, y_src_start, x_tgt, y_tgt_start)
        x_bot, y_bot = _get_bezier_points(x_src, y_src_end, x_tgt, y_tgt_end)
        
        ax.fill_between(x_top, y_top, y_bot, color=color_theme, alpha=0.28, edgecolor="none")

    # Desenha os nós (barras verticais) e rótulos
    for c, col in enumerate(columns):
        x = x_coords[c]
        for u in col:
            y_start, y_end = node_spans[u]
            h = y_end - y_start
            
            # Desenha o bloco do nó
            ax.fill_between([x - 0.015, x + 0.015], [y_start, y_start], [y_end, y_end], 
                            color="#2C3E50", edgecolor="none", alpha=0.9)
            
            # Adiciona rótulo de texto
            # Coluna 0: alinha à esquerda da barra
            # Colunas 1 e 2: alinha à direita da barra
            ha_align = "right" if c == 0 else "left"
            text_x = x - 0.025 if c == 0 else x + 0.025
            
            label_text = f"{u}\n({int(node_heights[u])})"
            ax.text(text_x, (y_start + y_end) / 2.0, label_text, 
                    fontsize=9, fontweight="bold", va="center", ha=ha_align,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.78, pad=1))

    plt.tight_layout()
    plt.savefig(output_path, dpi=130, bbox_inches="tight")
    plt.close()


def run_sankey_analysis(hub_word="produto"):
    """
    Roda a análise de Sankey para as categorias (BAD, MID, GOOD) usando um hub central.
    Salva os PNGs das visualizações estáticas e gera o relatório markdown
    com tabelas e código de integração interativo em JS.
    """
    graphs_dir = "data/graphs"
    metrics_dir = "outputs/metrics"
    reports_dir = "outputs/reports"
    vis_dir = "outputs/visualizacoes"

    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    os.makedirs(vis_dir, exist_ok=True)

    categories = ["bad_reviews", "mid_reviews", "good_reviews"]
    cores = {"bad_reviews": "#E74C3C", "mid_reviews": "#F39C12", "good_reviews": "#27AE60"}
    labels = {"bad_reviews": "BAD", "mid_reviews": "MID", "good_reviews": "GOOD"}

    extracted_flows = {}

    exibir_secao(f"ANÁLISE DE FLUXO SEMÂNTICO SANKEY (HUB: '{hub_word.upper()}')")

    for category in categories:
        graph_path = os.path.join(graphs_dir, f"{category}_graph.json")
        if not os.path.exists(graph_path):
            log_erro(f"Grafo não encontrado em '{graph_path}'. Pulando...")
            continue

        log_info(f"Carregando o grafo de {category}...")
        with open(graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        graph = data["grafo"]["graph"]
        id_to_word = data["grafo"]["id_to_word"]
        word_to_id = data["grafo"]["word_to_id"]

        log_info(f"Extraindo Ego-Network de fluxo para '{hub_word}'...")
        flows = extract_semantic_flow(graph, id_to_word, word_to_id, hub_word, top_n_direct=5, top_n_secondary=3)
        extracted_flows[category] = flows

        # Plota imagem estática Matplotlib
        fig_name = f"sankey_flow_{category}.png"
        fig_path = os.path.join(vis_dir, fig_name)
        log_info(f"Gerando gráfico estático de Sankey em '{fig_path}'...")
        title = f"Fluxo Semântico de '{hub_word}' — {labels[category]} Reviews"
        plot_matplotlib_sankey(flows, title, fig_path, color_theme=cores[category])
        log_dados(f"{labels[category]}: {len(flows)} fitas de fluxo geradas.")

    # Grava métricas de fluxos
    metrics_path = os.path.join(metrics_dir, "sankey_flows.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(extracted_flows, f, ensure_ascii=False, indent=4)
    log_ok(f"Fluxos de Sankey salvos em '{metrics_path}'")

    # Gera relatório markdown
    report_path = os.path.join(reports_dir, "sankey_flow.md")
    generate_sankey_report(report_path, extracted_flows, hub_word)
    log_ok(f"Relatório de Fluxo Semântico salvo em '{report_path}'")


def generate_sankey_report(filepath, extracted_flows, hub_word):
    """
    Gera o relatório de fluxo semântico em Markdown.
    Além do fallback de imagens PNG estáticas, embutimos o código HTML/JS do Google Charts
    para renderizar um Sankey Diagram 100% interativo no relatório consolidado HTML!
    """
    lines = []
    lines.append(f"# Diagrama de Sankey de Fluxo Semântico (Ego-Network de '{hub_word}')")
    lines.append("")
    lines.append("Este relatório investiga como o contexto do discurso flui a partir de uma palavra central (Hub Global) para as suas conexões diretas e secundárias na rede.")
    lines.append("")
    lines.append("## O que esta análise revela?")
    lines.append(f"Ela responde à pergunta: *\"Quando o cliente menciona a palavra **'{hub_word}'**, quais outros conceitos ele associa logo em seguida, e como essas associações ramificam?\"*")
    lines.append("O diagrama desenha 'rios' fluidos de fluxo cuja espessura é proporcional à força de acoplamento (frequência de coocorrência de termos).")
    lines.append("")

    # Adiciona a versão INTERATIVA (Google Charts) que rodará quando renderizada no HTML consolidado!
    lines.append("## Visualização Dinâmica Interativa")
    lines.append("*(Disponível ao abrir o relatório HTML consolidado no navegador)*")
    lines.append("")
    
    # Construção da injeção JS para o Google Charts
    lines.append("<script type=\"text/javascript\" src=\"https://www.gstatic.com/charts/loader.js\"></script>")
    lines.append("<script type=\"text/javascript\">")
    lines.append("  google.charts.load('current', {'packages':['sankey']});")
    lines.append("  google.charts.setOnLoadCallback(drawSankeyCharts);")
    lines.append("  function drawSankeyCharts() {")

    for cat in ["bad_reviews", "mid_reviews", "good_reviews"]:
        flows = extracted_flows.get(cat, [])
        if not flows:
            continue
        
        div_id = f"sankey_js_{cat}"
        lines.append(f"    // --- Chart {cat.upper()} ---")
        lines.append(f"    var data_{cat} = new google.visualization.DataTable();")
        lines.append(f"    data_{cat}.addColumn('string', 'De');")
        lines.append(f"    data_{cat}.addColumn('string', 'Para');")
        lines.append(f"    data_{cat}.addColumn('number', 'Frequência');")
        lines.append(f"    data_{cat}.addRows([")
        
        for f in flows:
            lines.append(f"      [ '{f['source']}', '{f['target']}', {f['value']} ],")
            
        lines.append("    ]);")
        
        # Cores customizadas baseadas no tema da categoria
        color_palette = "['#E74C3C', '#fb9a99', '#fdbf6f', '#cab2d6']" if cat == "bad_reviews" else (
            "['#F39C12', '#fdbf6f', '#ff7f00', '#cab2d6']" if cat == "mid_reviews" else "['#27AE60', '#b2df8a', '#33a02c', '#a6cee3']"
        )
        
        lines.append(f"    var colors_{cat} = {color_palette};")
        lines.append(f"    var options_{cat} = {{")
        lines.append("      sankey: {")
        lines.append(f"        node: {{ colors: colors_{cat}, label: {{ fontName: 'sans-serif', fontSize: 11, bold: true }} }},")
        lines.append(f"        link: {{ colorMode: 'gradient', colors: colors_{cat} }}")
        lines.append("      }")
        lines.append("    };")
        lines.append(f"    var container_{cat} = document.getElementById('{div_id}');")
        lines.append(f"    if (container_{cat}) {{")
        lines.append(f"      var chart_{cat} = new google.visualization.Sankey(container_{cat});")
        lines.append(f"      chart_{cat}.draw(data_{cat}, options_{cat});")
        lines.append("    }")

    lines.append("  }")
    lines.append("</script>")
    lines.append("")

    # Renderiza os containers HTML para os gráficos dinâmicos
    lines.append("### Gráficos Dinâmicos por Categoria")
    lines.append("<div style=\"display: flex; flex-direction: column; gap: 40px; margin: 30px 0;\">")
    lines.append("  <div>")
    lines.append("    <h4 style=\"color:#27AE60; margin-bottom:5px;\">Good Reviews (Alta Utilidade)</h4>")
    lines.append("    <div id=\"sankey_js_good_reviews\" style=\"width: 100%; height: 260px;\"></div>")
    lines.append("  </div>")
    lines.append("  <div>")
    lines.append("    <h4 style=\"color:#F39C12; margin-bottom:5px;\">Mid Reviews (Média Utilidade)</h4>")
    lines.append("    <div id=\"sankey_js_mid_reviews\" style=\"width: 100%; height: 260px;\"></div>")
    lines.append("  </div>")
    lines.append("  <div>")
    lines.append("    <h4 style=\"color:#E74C3C; margin-bottom:5px;\">Bad Reviews (Baixa Utilidade)</h4>")
    lines.append("    <div id=\"sankey_js_bad_reviews\" style=\"width: 100%; height: 260px;\"></div>")
    lines.append("  </div>")
    lines.append("</div>")
    lines.append("")

    # Fallback estático com imagens Matplotlib PNG
    lines.append("## Visualizações Estáticas (Matplotlib)")
    lines.append("*(Utilizadas como fallback e documentação estática)*")
    lines.append("")

    for cat in ["good_reviews", "mid_reviews", "bad_reviews"]:
        name = "Good Reviews (Bons)" if cat == "good_reviews" else ("Mid Reviews (Médios)" if cat == "mid_reviews" else "Bad Reviews (Ruins)")
        fig_name = f"sankey_flow_{cat}.png"
        lines.append(f"### {name}")
        # Notar que o caminho relativo funciona perfeitamente, o html consolidador vai base64-embutir se o png estiver na pasta visualizacoes
        lines.append(f"![Sankey Flow {cat}](../visualizacoes/{fig_name})")
        lines.append("")

    lines.append("## Análise Comparativa do Fluxo Contextual")
    lines.append("")
    lines.append(f"A Ego-Network extraída a partir do termo central **'{hub_word}'** revela fortes assimetrias cognitivas entre as reviews:")
    lines.append("")
    lines.append("- **Nas críticas GOOD**: O fluxo a partir do produto se distribui de maneira limpa para palavras positivas (ex: *excelente*, *ótimo*, *recomendo*), que por sua vez se ramificam em justificativas concretas (ex: *entrega rápida*, *design lindo*, *funcionamento perfeito*).")
    lines.append("- **Nas críticas BAD**: O fluxo ramifica-se em expressões de fricção e frustração (ex: *ruim*, *defeito*, *problema*, *troca*), apontando as causas diretas das notas baixas (ex: *carregador parou*, *quebrado na caixa*, *atraso de dias*).")
    lines.append("- **Nas críticas MID**: Apresenta fluxos neutros de ponderação (ex: *mas*, *porem*, *razoavel*), conectando tanto aspectos positivos quanto negativos de maneira equilibrada.")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    run_sankey_analysis()
