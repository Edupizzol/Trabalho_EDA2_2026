import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.analysis.pagerank import PageRankCalculator
from src.interface.console import exibir_secao, log_info, log_ok, log_aviso


def run_review_quality_ranking(top_k=20):
    """
    Gera um ranking de palavras associadas a reviews 'boas' vs 'ruins', com base
    no deslocamento de PageRank entre as categorias GOOD e BAD.

    Score diferencial = PageRank_em_GOOD - PageRank_em_BAD
    Palavras com score alto e positivo: fortemente associadas a reviews boas.
    Palavras com score alto e negativo: fortemente associadas a reviews ruins.

    A ideia prática: se uma palavra tem alto PageRank em reviews boas mas baixo
    (ou ausente) em reviews ruins, ela é um indicativo do tipo de conteúdo que
    torna uma review mais "útil"/bem avaliada -- então serve como um guia de
    quais aspectos vale a pena mencionar ao escrever uma review.
    """
    graphs_dir = "data/graphs"
    reports_dir = "outputs/reports"
    os.makedirs(reports_dir, exist_ok=True)

    calc_pr = PageRankCalculator()

    exibir_secao("RANKING DE QUALIDADE DE REVIEW (DESLOCAMENTO PAGERANK)")

    scores_por_categoria = {}
    for cat in ["good_reviews", "bad_reviews", "mid_reviews"]:
        graph_path = os.path.join(graphs_dir, f"{cat}_graph.json")
        if not os.path.exists(graph_path):
            log_aviso(f"Grafo de {cat} não encontrado. Pulando análise.")
            return
        with open(graph_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        graph_dict = data["grafo"]["graph"]
        id_to_word = data["grafo"]["id_to_word"]
        scores_por_categoria[cat] = calc_pr.calculate(graph_dict, id_to_word)

    scores_good = scores_por_categoria["good_reviews"]
    scores_bad = scores_por_categoria["bad_reviews"]

    vocabulario_uniao = set(scores_good.keys()).union(set(scores_bad.keys()))

    diferenciais = []
    for palavra in vocabulario_uniao:
        score_good = scores_good.get(palavra, 0.0)
        score_bad = scores_bad.get(palavra, 0.0)
        diff = score_good - score_bad
        diferenciais.append((palavra, score_good, score_bad, diff))

    diferenciais.sort(key=lambda x: x[3], reverse=True)
    top_boas = diferenciais[:top_k]

    diferenciais.sort(key=lambda x: x[3])
    top_ruins = diferenciais[:top_k]

    log_info(f"Top {top_k} palavras associadas a boas reviews calculadas.")

    # --- Montagem do relatório Markdown ---
    md_lines = [
        "# Guia de Palavras para uma Review Útil",
        "",
        "Este relatório usa o **deslocamento de PageRank** entre reviews boas e ruins "
        "para identificar quais palavras estão mais fortemente associadas a cada perfil "
        "de avaliação.",
        "",
        "**Metodologia:** para cada palavra do vocabulário, calculamos "
        "`score = PageRank(em reviews boas) - PageRank(em reviews ruins)`. "
        "Palavras com score alto e positivo aparecem com destaque em reviews boas e "
        "pouco (ou nada) em reviews ruins — são, portanto, indicativas do tipo de "
        "conteúdo que torna uma avaliação mais informativa e bem percebida.",
        "",
        "---",
        "",
        f"## ✅ Top {top_k} Palavras Associadas a Reviews Boas",
        "",
        "Se você quer escrever uma review percebida como útil, considere mencionar "
        "aspectos relacionados a estes termos:",
        "",
        "| Rank | Palavra | PageRank (Good) | PageRank (Bad) | Score Diferencial |",
        "| :---: | :--- | :---: | :---: | :---: |",
    ]
    for i, (palavra, sg, sb, diff) in enumerate(top_boas, 1):
        md_lines.append(f"| {i} | **{palavra}** | {sg:.5f} | {sb:.5f} | +{diff:.5f} |")

    md_lines.extend([
        "",
        "---",
        "",
        f"## ⚠️ Top {top_k} Palavras Associadas a Reviews Ruins",
        "",
        "Estes termos têm presença forte em reviews mal avaliadas e fraca (ou nula) "
        "em reviews boas — geralmente relacionados a falhas, defeitos ou frustrações:",
        "",
        "| Rank | Palavra | PageRank (Good) | PageRank (Bad) | Score Diferencial |",
        "| :---: | :--- | :---: | :---: | :---: |",
    ])
    for i, (palavra, sg, sb, diff) in enumerate(top_ruins, 1):
        md_lines.append(f"| {i} | **{palavra}** | {sg:.5f} | {sb:.5f} | {diff:.5f} |")

    md_lines.extend([
        "",
        "---",
        "",
        "## Interpretação",
        "As palavras do primeiro grupo formam, na prática, um *checklist* informal: "
        "reviews que mencionam características concretas e descritivas do produto "
        "(em vez de opiniões genéricas) tendem a se aproximar do perfil de discurso "
        "encontrado em avaliações bem-recebidas. O segundo grupo, por outro lado, "
        "reflete os pontos de fricção mais recorrentes — vale observá-los como sinais "
        "de alerta sobre o que normalmente frustra outros consumidores.",
        ""
    ])

    report_path = os.path.join(reports_dir, "guia_boa_review.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    log_ok(f"Guia de qualidade de review salvo em: '{report_path}'")


if __name__ == "__main__":
    run_review_quality_ranking()