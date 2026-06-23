"""
Consolidação de resultados em um único relatório HTML.

Varre os artefatos gerados pelas análises (Markdown + PNG) espalhados em
`outputs/` e os reúne em uma página HTML autocontida (imagens embutidas em
base64), com índice de navegação. Lê apenas o que existir no momento da
execução — portanto reflete "todas as análises feitas até então".

Fontes de conteúdo:
  outputs/menu/opcao{1,2,3}/resultado_execucao.md   (+ PNGs)
  outputs/menu/opcao{1,2,3}/analise_diferencial.md
  outputs/reports/pagerank_comparison.md
  outputs/reports/bfs_semantic_context.md
"""

import os
import re
import glob
import shutil
import base64
from datetime import datetime
from pathlib import Path

import markdown

from src.interface.console import exibir_secao, log_info, log_ok, log_aviso, console


# Diretórios e nomes amigáveis das três opções de escopo.
_ESCOPOS = {
    "opcao1": "Amostragem Rápida (100 reviews por faixa)",
    "opcao2": "Seleção Manual (curadoria)",
    "opcao3": "Escopo Total (dataset completo)",
}

_EXTENSOES_MD = ["tables", "fenced_code", "sane_lists"]


# ── Utilidades de imagem ─────────────────────────────────────────────────────

def _png_para_base64(caminho_png: str) -> str:
    with open(caminho_png, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _embutir_imagens(md_texto: str, base_dir: str) -> str:
    """
    Substitui referências a PNGs (tanto `<img src='...'>` quanto `![](...)`)
    por data URIs base64, tornando o HTML final autocontido.
    """

    def _b64_de(nome_arquivo: str):
        caminho = os.path.join(base_dir, os.path.basename(nome_arquivo))
        if not os.path.exists(caminho):
            return None
        return _png_para_base64(caminho)

    def _repl_html(m):
        b64 = _b64_de(m.group(1))
        if b64 is None:
            return m.group(0)
        return f'src="data:image/png;base64,{b64}"'

    md_texto = re.sub(r"src=['\"]([^'\"]+\.png)['\"]", _repl_html, md_texto)

    def _repl_md(m):
        alt, nome = m.group(1), m.group(2)
        b64 = _b64_de(nome)
        if b64 is None:
            return m.group(0)
        return f'<img alt="{alt}" src="data:image/png;base64,{b64}"/>'

    md_texto = re.sub(r"!\[([^\]]*)\]\(([^)]+\.png)\)", _repl_md, md_texto)
    return md_texto


# ── Conversão Markdown → HTML ────────────────────────────────────────────────

def _md_arquivo_para_html(caminho_md: str) -> str:
    """Lê um arquivo Markdown, embute as imagens e converte para HTML."""
    base_dir = os.path.dirname(caminho_md)
    with open(caminho_md, "r", encoding="utf-8") as f:
        texto = f.read()
    texto = _embutir_imagens(texto, base_dir)
    return markdown.markdown(texto, extensions=_EXTENSOES_MD)


# ── Montagem das seções ──────────────────────────────────────────────────────

def _coletar_secoes():
    """
    Varre os outputs e devolve uma lista de seções:
    cada item é (id_ancora, titulo, html_conteudo).
    """
    secoes = []

    # 1. Resultados por escopo (opção 1, 2, 3).
    for pasta, nome_amigavel in _ESCOPOS.items():
        dir_opcao = os.path.join("outputs", "menu", pasta)
        if not os.path.isdir(dir_opcao):
            continue

        partes_html = []
        md_resultado = os.path.join(dir_opcao, "resultado_execucao.md")
        md_diferencial = os.path.join(dir_opcao, "analise_diferencial.md")

        if os.path.exists(md_resultado):
            partes_html.append(_md_arquivo_para_html(md_resultado))
        if os.path.exists(md_diferencial):
            partes_html.append(_md_arquivo_para_html(md_diferencial))

        if partes_html:
            secoes.append((pasta, nome_amigavel, "\n<hr/>\n".join(partes_html)))
            log_info(f"Escopo incluído: {nome_amigavel}")

    # 2. Relatório de PageRank.
    md_pagerank = os.path.join("outputs", "reports", "pagerank_comparison.md")
    if os.path.exists(md_pagerank):
        secoes.append(("pagerank", "Análise de PageRank", _md_arquivo_para_html(md_pagerank)))
        log_info("Relatório de PageRank incluído.")

    # 3. Relatório de BFS.
    md_bfs = os.path.join("outputs", "reports", "bfs_semantic_context.md")
    if os.path.exists(md_bfs):
        secoes.append(("bfs", "Vizinhança Semântica (BFS)", _md_arquivo_para_html(md_bfs)))
        log_info("Relatório de BFS incluído.")

    # 4. Relatório de K-Core.
    md_kcore = os.path.join("outputs", "reports", "kcore_decomposition.md")
    if os.path.exists(md_kcore):
        secoes.append(("kcore", "Decomposição K-Core", _md_arquivo_para_html(md_kcore)))
        log_info("Relatório de K-Core incluído.")

    # 5. Relatório de Sankey.
    md_sankey = os.path.join("outputs", "reports", "sankey_flow.md")
    if os.path.exists(md_sankey):
        secoes.append(("sankey", "Fluxo Semântico (Sankey)", _md_arquivo_para_html(md_sankey)))
        log_info("Relatório de Fluxo Semântico (Sankey) incluído.")

    # 6. Visualizações Avançadas (Etapa 3) — um MD por gráfico, em ordem fixa.
    vis_dir = os.path.join("outputs", "visualizacoes")
    _ORDEM_VIS = [
        ("distribuicao_grau",    "Distribuição de Grau"),
        ("comparativo_top10",    "Comparativo Top 10 (PageRank)"),
        ("heatmap_coocorrencia", "Heatmap de Coocorrência"),
        ("scatter_deslocamento", "Scatter de Deslocamento"),
        ("wordcloud_pagerank",   "Word Cloud (PageRank)"),
        ("kcore_target_chart",   "Gráfico de Alvo (K-Core)"),
        ("sankey_flow_chart",    "Diagramas de Sankey Estáticos"),
    ]
    partes_vis = []
    for slug, titulo_vis in _ORDEM_VIS:
        md_path = os.path.join(vis_dir, f"{slug}.md")
        if os.path.exists(md_path):
            partes_vis.append(_md_arquivo_para_html(md_path))
            log_info(f"Visualização incluída: {titulo_vis}")

    if partes_vis:
        secoes.append(("visualizacoes", "Visualizações Avançadas (Etapa 3)",
                        "\n<hr/>\n".join(partes_vis)))

    return secoes


# ── Template HTML ────────────────────────────────────────────────────────────

_CSS = """
:root {
  --cor-primaria: #1F78B4;
  --cor-secundaria: #FF4500;
  --texto: #2b2b2b;
  --texto-suave: #5a5a5a;
  --borda: #e2e2e2;
  --fundo: #ffffff;
  --fundo-nav: #f7f9fb;
  --fundo-codigo: #f3f4f6;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: var(--texto);
  background: var(--fundo);
  line-height: 1.6;
}
.layout { display: flex; min-height: 100vh; }
nav.sumario {
  width: 280px;
  flex-shrink: 0;
  background: var(--fundo-nav);
  border-right: 1px solid var(--borda);
  padding: 24px 18px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}
nav.sumario h2 {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--texto-suave);
  margin: 0 0 12px;
}
nav.sumario a {
  display: block;
  padding: 8px 12px;
  margin-bottom: 4px;
  border-radius: 6px;
  color: var(--texto);
  text-decoration: none;
  font-size: 14px;
  transition: background 0.15s, color 0.15s;
}
nav.sumario a:hover { background: #e8eef4; color: var(--cor-primaria); }
main { flex: 1; padding: 40px 56px; max-width: 1000px; margin: 0 auto; }
header.capa {
  border-bottom: 3px solid var(--cor-primaria);
  padding-bottom: 20px;
  margin-bottom: 16px;
}
header.capa h1 { margin: 0 0 6px; font-size: 30px; }
header.capa .meta { color: var(--texto-suave); font-size: 14px; }
section.bloco { margin: 48px 0; scroll-margin-top: 20px; }
section.bloco > h2.titulo-secao {
  font-size: 22px;
  color: var(--cor-primaria);
  border-left: 4px solid var(--cor-primaria);
  padding-left: 12px;
  margin-bottom: 20px;
}
h1, h2, h3, h4 { line-height: 1.3; }
.conteudo h1 { font-size: 22px; margin-top: 28px; }
.conteudo h2 { font-size: 19px; margin-top: 26px; }
.conteudo h3 { font-size: 16px; margin-top: 22px; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
  font-size: 14px;
}
th, td { border: 1px solid var(--borda); padding: 8px 10px; text-align: left; }
th { background: var(--fundo-nav); font-weight: 600; }
tr:nth-child(even) td { background: #fafbfc; }
img { max-width: 100%; height: auto; border-radius: 6px; }
code {
  background: var(--fundo-codigo);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
hr { border: none; border-top: 1px solid var(--borda); margin: 32px 0; }
.vazio { color: var(--texto-suave); font-style: italic; }
footer { margin-top: 60px; padding-top: 20px; border-top: 1px solid var(--borda); color: var(--texto-suave); font-size: 13px; }
@media (max-width: 820px) {
  .layout { flex-direction: column; }
  nav.sumario { width: 100%; height: auto; position: static; border-right: none; border-bottom: 1px solid var(--borda); }
  main { padding: 24px 20px; }
}
"""


def _montar_html(secoes) -> str:
    gerado_em = datetime.now().strftime("%d/%m/%Y às %H:%M")

    # Índice de navegação.
    itens_nav = "\n".join(
        f'      <a href="#{sid}">{titulo}</a>' for sid, titulo, _ in secoes
    )

    # Blocos de conteúdo.
    blocos = []
    for sid, titulo, html in secoes:
        blocos.append(
            f'    <section class="bloco" id="{sid}">\n'
            f'      <h2 class="titulo-secao">{titulo}</h2>\n'
            f'      <div class="conteudo">{html}</div>\n'
            f'    </section>'
        )
    blocos_html = "\n".join(blocos)

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Relatório Consolidado — Análise de Reviews</title>
  <style>{_CSS}</style>
</head>
<body>
  <div class="layout">
    <nav class="sumario">
      <h2>Sumário</h2>
{itens_nav}
    </nav>
    <main>
      <header class="capa">
        <h1>Relatório Consolidado de Análise</h1>
        <div class="meta">
          Análise de Utilidade em Reviews de E-commerce via Grafos de Coocorrência<br/>
          Gerado em {gerado_em}
        </div>
      </header>
{blocos_html}
      <footer>
        Documento gerado automaticamente a partir dos artefatos de análise (Markdown + PNG).
        Trabalho de Estruturas de Dados e Algoritmos II (EDA II).
      </footer>
    </main>
  </div>
</body>
</html>
"""


# ── Função pública ───────────────────────────────────────────────────────────

def limpar_artefatos_de_analise():
    """
    Remove os artefatos gerados em execuções anteriores (resultados por escopo,
    relatórios de PageRank/BFS, métricas e o HTML consolidado).

    Deve ser chamada no início de uma nova Etapa 1 (seleção de escopo) para que
    o relatório consolidado reflita APENAS o ciclo atual — primeiro só o conteúdo
    da Etapa 1 e, em seguida, acrescentando o que a Etapa 2 produzir.
    Os arquivos `.gitkeep` das pastas são preservados.
    """
    for pasta in (
        os.path.join("outputs", "menu"),
        os.path.join("outputs", "visualizacoes"),
    ):
        if os.path.isdir(pasta):
            shutil.rmtree(pasta)

    for padrao in (
        os.path.join("outputs", "reports", "*.md"),
        os.path.join("outputs", "metrics", "*.json"),
    ):
        for caminho in glob.glob(padrao):
            os.remove(caminho)

    html_anterior = os.path.join("outputs", "relatorio_consolidado.html")
    if os.path.exists(html_anterior):
        os.remove(html_anterior)


def gerar_relatorio_html(output_path: str = "outputs/relatorio_consolidado.html") -> bool:
    """
    Gera o relatório HTML consolidado a partir dos outputs existentes.
    Retorna True se o relatório foi gerado, False se não havia análises.
    """
    exibir_secao("GERAÇÃO DE RELATÓRIO HTML CONSOLIDADO")

    secoes = _coletar_secoes()
    if not secoes:
        log_aviso("Nenhum resultado encontrado em 'outputs/'. Rode ao menos uma análise antes.")
        return False

    html = _montar_html(secoes)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    log_ok(f"Relatório consolidado gerado em '{output_path}' ({len(secoes)} seções)")

    # Exibe um link clicável (hyperlink OSC 8) para abrir o HTML no navegador.
    # Terminais modernos (Windows Terminal, etc.) tornam o caminho clicável.
    html_uri = Path(output_path).resolve().as_uri()
    console.print(
        f"  [dim]→ Abrir no navegador:[/] "
        f"[link={html_uri}][cyan underline]{output_path}[/cyan underline][/link]"
    )

    return True


if __name__ == "__main__":
    gerar_relatorio_html()
