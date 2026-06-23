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

    # 4. Relatório de DFS (componentes conexos) 
    md_dfs = os.path.join("outputs", "reports", "dfs_components.md")
    if os.path.exists(md_dfs):
        secoes.append(("dfs", "Fragmentação Semântica (DFS)", _md_arquivo_para_html(md_dfs)))
        log_info("Relatório de DFS incluído.")

    md_guia = os.path.join("outputs", "reports", "guia_boa_review.md")
    if os.path.exists(md_guia):
        secoes.append(("guia_review", "Guia de Boa Review", _md_arquivo_para_html(md_guia)))
        log_info("Guia de boa review incluído.")

    # 5. Visualizações Avançadas (Etapa 3) — um MD por gráfico, em ordem fixa.
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
  --brand-red: #E60014;
  --brand-red-dark: #A8000E;
  --brand-red-light: #FFF1F2;
  --brand-yellow: #FFD400;
  --brand-blue: #00ADEF;
  --brand-orange: #FF6600;
  
  --primary: #0F172A;
  --primary-hover: #1E293B;
  --primary-light: #F1F5F9;
  --accent: #E60014;
  --bg-app: #F4F6F9;
  --bg-card: #FFFFFF;
  --text-main: #1E293B;
  --text-muted: #64748B;
  --border: #E2E8F0;
  --radius-lg: 16px;
  --radius-md: 12px;
  --radius-sm: 8px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
  --shadow-md: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.08), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Inter', -apple-system, sans-serif;
  color: var(--text-main);
  background-color: var(--bg-app);
  line-height: 1.6;
  font-size: 15px;
  -webkit-font-smoothing: antialiased;
}

.layout {
  display: flex;
  min-height: 100vh;
}

nav.sumario {
  width: 290px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-right: 1px solid var(--border);
  padding: 30px 16px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  z-index: 10;
}

.logo-container {
  margin-bottom: 30px;
  padding: 0 12px;
}

.brand-b2w {
  display: block;
  font-family: 'Outfit', sans-serif;
  font-size: 20px;
  font-weight: 800;
  text-transform: lowercase;
  letter-spacing: 0.03em;
  color: var(--brand-red);
}

.brand-b2w span {
  color: var(--primary);
  font-weight: 400;
}

.brand-sub {
  display: block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.15em;
  margin-top: 2px;
}

nav.sumario h2 {
  font-family: 'Outfit', sans-serif;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin: 0 0 12px 12px;
}

nav.sumario a {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  margin-bottom: 6px;
  border-radius: var(--radius-sm);
  color: var(--text-main);
  font-weight: 500;
  text-decoration: none;
  font-size: 14px;
  transition: var(--transition);
}

nav.sumario a:hover {
  background-color: var(--brand-red-light);
  color: var(--brand-red);
  transform: translateX(4px);
}

.nav-icon {
  flex-shrink: 0;
  opacity: 0.6;
  transition: var(--transition);
}

nav.sumario a:hover .nav-icon {
  opacity: 1;
  color: var(--brand-red);
}

main {
  flex: 1;
  padding: 0 48px 48px 48px;
  max-width: 1120px;
  margin: 0 auto;
}

/* Brand bar style */
.brand-bar {
  background: var(--bg-app);
  border-bottom: 1px solid var(--border);
  padding: 16px 0;
  margin-bottom: 30px;
  position: sticky;
  top: 0;
  z-index: 5;
}

.brand-bar-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-logo {
  font-family: 'Outfit', sans-serif;
  font-weight: 800;
  font-size: 18px;
  color: var(--brand-red);
  text-transform: lowercase;
  letter-spacing: -0.02em;
}

.brand-logo .brand-tag {
  background: var(--brand-red-light);
  color: var(--brand-red);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 999px;
  margin-left: 8px;
  letter-spacing: 0.05em;
  vertical-align: middle;
}

.search-mock {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--primary-light);
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  width: 320px;
  border: 1px solid transparent;
  transition: var(--transition);
}

.search-mock input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 13px;
  width: 100%;
  color: var(--text-main);
}

.search-mock svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-profile .avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--brand-red);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  font-family: 'Outfit', sans-serif;
}

.user-profile .user-details {
  display: flex;
  flex-direction: column;
}

.user-profile .user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
  line-height: 1.2;
}

.user-profile .user-role {
  font-size: 11px;
  color: var(--text-muted);
}

header.capa {
  background: linear-gradient(135deg, var(--brand-red-dark) 0%, var(--brand-red) 100%);
  color: white;
  border-radius: var(--radius-lg);
  padding: 48px;
  margin-bottom: 30px;
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

header.capa::after {
  content: "";
  position: absolute;
  top: -60px;
  right: -60px;
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0) 70%);
  border-radius: 50%;
}

header.capa h1 {
  font-family: 'Outfit', sans-serif;
  margin: 0 0 10px;
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
  color: #FFFFFF;
}

header.capa .meta {
  opacity: 0.95;
  font-size: 14px;
  line-height: 1.7;
}

/* Dashboard KPIs Grid */
.dashboard-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.kpi-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--brand-red);
}

.kpi-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-data {
  display: flex;
  flex-direction: column;
}

.kpi-value {
  font-family: 'Outfit', sans-serif;
  font-size: 20px;
  font-weight: 800;
  color: var(--primary);
  line-height: 1.2;
}

.kpi-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-main);
  margin-top: 2px;
}

.kpi-sub {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 1px;
}

/* Review Wall styles */
.review-wall-title {
  font-family: 'Outfit', sans-serif;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  margin: 10px 0 15px 4px;
}

.review-wall {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.review-item {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: var(--transition);
}

.review-item:hover {
  box-shadow: var(--shadow-md);
}

.review-item.good { border-left: 4px solid #10B981; }
.review-item.mid { border-left: 4px solid #F59E0B; }
.review-item.bad { border-left: 4px solid #EF4444; }

.review-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.review-item .stars {
  font-size: 14px;
  color: var(--brand-yellow);
  letter-spacing: 2px;
}

.review-item .badge {
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 999px;
}

.review-item .badge.good { background: #D1FAE5; color: #065F46; }
.review-item .badge.mid { background: #FEF3C7; color: #92400E; }
.review-item .badge.bad { background: #FEE2E2; color: #991B1B; }

.review-body {
  font-size: 13.5px;
  color: var(--text-main);
  line-height: 1.5;
  font-style: italic;
}

.review-body strong {
  color: var(--brand-red);
  font-style: normal;
  background: var(--brand-red-light);
  padding: 0 4px;
  border-radius: 2px;
}

.review-meta {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 12px;
  text-align: right;
}

section.bloco {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  padding: 40px;
  margin: 30px 0;
  scroll-margin-top: 90px;
  box-shadow: var(--shadow-sm);
  transition: var(--transition);
}

section.bloco:hover {
  box-shadow: var(--shadow-md);
}

section.bloco > h2.titulo-secao {
  font-family: 'Outfit', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: var(--primary);
  margin-top: 0;
  margin-bottom: 24px;
  border-bottom: 2px solid var(--primary-light);
  padding-bottom: 12px;
  position: relative;
}

section.bloco > h2.titulo-secao::after {
  content: "";
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, var(--brand-red), var(--brand-blue));
}

h1, h2, h3, h4 {
  font-family: 'Outfit', sans-serif;
  color: var(--primary);
  font-weight: 700;
}

.conteudo h1 { font-size: 20px; margin-top: 28px; margin-bottom: 14px; }
.conteudo h2 { font-size: 17px; margin-top: 24px; margin-bottom: 12px; }
.conteudo h3 { font-size: 15px; margin-top: 20px; margin-bottom: 10px; }

table {
  border-collapse: collapse;
  width: 100%;
  margin: 24px 0;
  font-size: 14px;
  box-shadow: var(--shadow-sm);
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border);
}

th, td {
  padding: 12px 16px;
  text-align: left;
}

th {
  background: var(--primary-light);
  color: var(--primary);
  font-family: 'Outfit', sans-serif;
  font-weight: 600;
  border-bottom: 2px solid var(--border);
}

td {
  border-bottom: 1px solid var(--border);
  color: var(--text-main);
  background: var(--bg-card);
}

tr:nth-child(even) td {
  background: #F8FAFC;
}

tr:hover td {
  background: #F1F5F9;
}

img {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  margin: 20px 0;
  transition: var(--transition);
}

img:hover {
  transform: scale(1.01);
  box-shadow: var(--shadow-md);
}

blockquote {
  border-left: 4px solid var(--brand-red);
  background: var(--brand-red-light);
  padding: 16px 20px;
  margin: 20px 0;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 14px;
  color: var(--brand-red-dark);
}

blockquote strong {
  color: var(--brand-red);
}

code {
  background: #F1F5F9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
  color: #BE185D;
}

pre {
  background: #0F172A;
  padding: 16px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 20px 0;
}

pre code {
  background: transparent;
  padding: 0;
  color: #F8FAFC;
  font-size: 13px;
}

hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 30px 0;
}

.vazio {
  color: var(--text-muted);
  font-style: italic;
}

footer {
  margin-top: 60px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #F1F5F9;
}
::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #94A3B8;
}

/* Smooth Scrolling */
html {
  scroll-behavior: smooth;
}

@media (max-width: 920px) {
  .layout {
    flex-direction: column;
  }
  nav.sumario {
    width: 100%;
    height: auto;
    position: static;
    border-right: none;
    border-bottom: 1px solid var(--border);
    padding: 20px;
  }
  nav.sumario a:hover {
    transform: translateY(2px);
  }
  main {
    padding: 0 20px 30px 20px;
  }
  .brand-bar {
    position: static;
  }
  .brand-bar-inner {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  .search-mock {
    width: 100%;
  }
}
"""


def _obter_icone_svg(sid: str) -> str:
    # Retorna o código SVG para o ícone correspondente ao ID da seção
    icons = {
        "opcao1": '<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>',
        "opcao2": '<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>',
        "opcao3": '<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line><line x1="15" y1="3" x2="15" y2="21"></line><line x1="3" y1="9" x2="21" y2="9"></line><line x1="3" y1="15" x2="21" y2="15"></line></svg>',
        "pagerank": '<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>',
        "bfs": '<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>',
        "kcore": '<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>',
        "sankey": '<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>',
        "visualizacoes": '<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="M12 6v6l4 2"></path></svg>'
    }
    return icons.get(sid, '<svg class="nav-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle></svg>')


def _montar_html(secoes) -> str:
    gerado_em = datetime.now().strftime("%d/%m/%Y às %H:%M")

    # Índice de navegação.
    itens_nav = "\n".join(
        f'      <a href="#{sid}">{_obter_icone_svg(sid)} <span>{titulo}</span></a>' for sid, titulo, _ in secoes
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
  <title>Painel CX Analytics — Lojas Americanas</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>{_CSS}</style>
</head>
<body>
  <div class="layout">
    <nav class="sumario">
      <div class="logo-container">
        <span class="brand-b2w">americanas <span>s.a.</span></span>
        <span class="brand-sub">cx analytics panel</span>
      </div>
      <h2>Navegação</h2>
{itens_nav}
    </nav>
    <main>
      <div class="brand-bar">
        <div class="brand-bar-inner">
          <span class="brand-logo">americanas s.a. <span class="brand-tag">cx analytics</span></span>
          <div class="search-mock">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input type="text" placeholder="Buscar termos na rede..." disabled />
          </div>
          <div class="user-profile">
            <div class="avatar">CX</div>
            <div class="user-details">
              <span class="user-name">Equipe de CX</span>
              <span class="user-role">Administrador</span>
            </div>
          </div>
        </div>
      </div>

      <header class="capa">
        <h1>Portal de Análise de Sentimentos</h1>
        <div class="meta">
          Análise de Utilidade em Reviews de E-commerce via Grafos de Coocorrência<br/>
          Gerado em {gerado_em}
        </div>
      </header>

      <div class="dashboard-kpis">
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background-color: var(--brand-red-light); color: var(--brand-red);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value">100.000+</span>
            <span class="kpi-label">Avaliações Analisadas</span>
            <span class="kpi-sub">Origem: Dataset B2W Group</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background-color: #E0F2FE; color: var(--brand-blue);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value">"produto"</span>
            <span class="kpi-label">Hub de Rede</span>
            <span class="kpi-sub">Ego-Network de Coocorrência</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background-color: #FEF3C7; color: #D97706;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value">Camada 6</span>
            <span class="kpi-label">Núcleo K-Core</span>
            <span class="kpi-sub">Resiliência do Discurso</span>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background-color: #D1FAE5; color: #059669;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
          </div>
          <div class="kpi-data">
            <span class="kpi-value">+74 NPS</span>
            <span class="kpi-label">Zona de Excelência</span>
            <span class="kpi-sub">Utilidade dos Feedbacks</span>
          </div>
        </div>
      </div>

      <div class="review-wall-title">Mural de Avaliações de Clientes (Reviews Reais do Dataset)</div>
      <div class="review-wall">
        <div class="review-item good">
          <div class="review-item-header">
            <span class="stars">★★★★★</span>
            <span class="badge good">Bons (Good)</span>
          </div>
          <div class="review-body">
            "Excelente <strong>produto</strong>, a entrega foi muito rápida e a <strong>qualidade</strong> da impressão do <strong>livro</strong> é fantástica pelo <strong>preço</strong> pago. Superou minha <strong>expectativa</strong>!"
          </div>
          <div class="review-meta">Cliente Americanas - SP</div>
        </div>
        <div class="review-item mid">
          <div class="review-item-header">
            <span class="stars">★★★☆☆</span>
            <span class="badge mid">Médios (Mid)</span>
          </div>
          <div class="review-body">
            "O <strong>produto</strong> atende às necessidades, mas o <strong>prazo</strong> de entrega foi longo e a <strong>embalagem</strong> veio um pouco amassada. Esperava um material mais resistente."
          </div>
          <div class="review-meta">Cliente Americanas - RJ</div>
        </div>
        <div class="review-item bad">
          <div class="review-item-header">
            <span class="stars">★☆☆☆☆</span>
            <span class="badge bad">Ruins (Bad)</span>
          </div>
          <div class="review-body">
            "Péssimo <strong>atendimento</strong>! O <strong>produto</strong> veio com defeito e o <strong>prazo</strong> limite de troca no <strong>site</strong> expirou sem retorno. Uma grande decepção com a compra."
          </div>
          <div class="review-meta">Cliente Americanas - MG</div>
        </div>
      </div>

{blocos_html}
      <footer>
        Documento gerado automaticamente a partir dos artefatos de análise (Markdown + PNG).<br/>
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
