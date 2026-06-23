

import questionary
from questionary import Choice, Style

from src.interface.console import console, exibir_painel, despedida

# Ações disparadas pelos menus.
from menu.opcao1.executor import executar_opcao_1
from menu.opcao2.executor import executar_opcao_2
from menu.opcao3.executor import executar_opcao_3
from src.analysis.pagerank_runner import run_pagerank_analysis
from src.analysis.bfs import run_bfs_analysis
from src.analysis.dfs import run_dfs_analysis
from src.analysis.visualizacoes import (
    gerar_distribuicao_grau,
    gerar_comparativo_top10,
    gerar_heatmap_coocorrencia,
    gerar_scatter_deslocamento,
    gerar_wordcloud_pagerank,
    run_todas_visualizacoes,
)
from src.reporting.html_consolidator import gerar_relatorio_html, limpar_artefatos_de_analise


# Estilo visual compartilhado pelos prompts do Questionary.
ESTILO = Style(
    [
        ("qmark", "fg:#00afaf bold"),
        ("question", "bold"),
        ("pointer", "fg:#ff8700 bold"),
        ("highlighted", "fg:#ff8700 bold"),
        ("selected", "fg:#00af5f"),
        ("answer", "fg:#00afaf bold"),
    ]
)


_TEXTO_ETAPA1 = (
    "As reviews são separadas em três faixas de satisfação "
    "([green]GOOD[/] / [yellow]MID[/] / [red]BAD[/]) e transformadas em "
    "grafos de coocorrência de palavras.\n\n"
    "Para [bold]cada[/] faixa, serão gerados automaticamente:\n"
    "  • Gráfico de barras com as 5 palavras mais influentes (PageRank)\n"
    "  • Visualização da rede de coocorrência semântica\n"
    "  • Relatório executivo  [dim]-> resultado_execucao.md[/]\n"
    "  • Análise diferencial  [dim]-> analise_diferencial.md[/]"
)

_TEXTO_ETAPA2 = (
    "Os grafos já foram construídos. Aprofunde a investigação:\n\n"
    "[bold]PageRank[/]\n"
    "  Ranqueia as palavras mais centrais de cada faixa em uma tabela\n"
    "  comparativa Top 15 (BAD / MID / GOOD).\n"
    "  [dim]\"Quais palavras dominam o discurso de cada nível?\"[/]\n\n"
    "[bold]BFS Contextual[/]\n"
    "  Explora a vizinhança de palavras-chave, mostrando com quais\n"
    "  termos elas mais coocorrem em cada faixa.\n"
    "  [dim]\"Em que contexto uma palavra aparece em cada nível?\"[/]\n\n"
    "[bold]DFS — Componentes Conexos[/]\n"
    "  Identifica blocos de palavras isolados do restante do vocabulário.\n"
    "  [dim]\"O discurso é unificado ou fragmentado em subtemas?\"[/]\n\n"
    "[dim]O relatório HTML consolidado é atualizado automaticamente\n"
    "após cada análise -> outputs/relatorio_consolidado.html[/]"
)

_TEXTO_ETAPA3 = (
    "Visualizações avançadas geradas a partir dos grafos e scores de PageRank:\n\n"
    "[bold]1.[/] Distribuição de Grau    [dim]— topologia geral da rede[/]\n"
    "[bold]2.[/] Comparativo Top 10      [dim]— relevância lado a lado entre BAD/MID/GOOD[/]\n"
    "[bold]3.[/] Heatmap de Coocorrência [dim]— combos semânticos entre os hubs[/]\n"
    "[bold]4.[/] Scatter de Deslocamento [dim]— palavras que mais discriminam satisfação[/]\n"
    "[bold]5.[/] Word Cloud (PageRank)   [dim]— impressão visual do vocabulário dominante[/]\n\n"
    "[dim]Cada gráfico gera um PNG + Markdown e é incluído no relatório HTML consolidado.[/]"
)


def _menu_escopo(cleaned_dir, processed_dir, carregar_func, salvar_func):
    """
    ETAPA 1 — Análise Principal.
    Apresenta o escopo dos dados e constrói os grafos de coocorrência.
    Retorna True se um grafo foi construído, False se o usuário saiu.
    """
    console.print()
    console.rule("[bold cyan]ETAPA 1 — Análise Principal (Construção dos Grafos)[/]", style="cyan")
    console.print()
    exibir_painel(_TEXTO_ETAPA1, "Escopo dos Dados", "cyan")

    escolha = questionary.select(
        "Escolha o ESCOPO dos dados que alimentará o grafo:",
        choices=[
            Choice("Amostragem Rápida — 100 reviews de cada faixa (recomendado p/ testes)", value="1"),
            Choice("Seleção Manual — você escolhe quais reviews entram no grafo", value="2"),
            Choice("Escopo Total — processa TODAS as reviews (mais lento e completo)", value="3"),
            Choice("Sair", value="0"),
        ],
        style=ESTILO,
    ).ask()

    if escolha in ("1", "2", "3"):
        # Cada nova Etapa 1 começa um ciclo limpo: remove artefatos de execuções
        # anteriores para que o relatório contenha SOMENTE o conteúdo deste ciclo.
        limpar_artefatos_de_analise()

        if escolha == "1":
            executar_opcao_1(cleaned_dir, processed_dir, carregar_func, salvar_func)
        elif escolha == "2":
            executar_opcao_2(cleaned_dir, processed_dir, carregar_func, salvar_func)
        else:
            executar_opcao_3(cleaned_dir, processed_dir)

        # Gera o relatório apenas com o conteúdo da Etapa 1.
        gerar_relatorio_html()
        return True

    # "0" ou None (Ctrl+C) → encerrar
    return False


def _menu_analises_adicionais():
    """
    ETAPA 2 — Análises Adicionais.
    Roda PageRank e BFS sobre os grafos já construídos.
    Retorna:
      "exit"   → encerrar o programa
      "back"   → voltar à Etapa 1 (reconstruir grafos)
      "stage3" → avançar para a Etapa 3 (visualizações avançadas)
    """
    console.print()
    console.rule("[bold magenta]ETAPA 2 — Análises Adicionais[/]", style="magenta")

    
    console.print()
    exibir_painel(_TEXTO_ETAPA2, "Opções de Análises Adicionais", "magenta")
    escolha = questionary.select(
            "O que deseja executar sobre os grafos construídos?",
            choices=[
                Choice("PageRank — palavras mais centrais (tabela comparativa Top 15)", value="4"),
                Choice("BFS Contextual — vizinhança semântica de palavras-chave", value="5"),
                Choice("DFS — componentes conexos (fragmentação do discurso)", value="8"),
                Choice("Execute Todas As Análises Adicionais (PageRank, BFS e DFS)", value="6"),
                Choice("Visualizações Avançadas — avançar para a Etapa 3", value="7"),
                Choice("Voltar — reconstruir o grafo com outro escopo", value="9"),
                Choice("Sair", value="0"),
            ],
            style=ESTILO,
        ).ask()

    if escolha == "4":
            run_pagerank_analysis()
            gerar_relatorio_html()
    elif escolha == "5":
            run_bfs_analysis()
            gerar_relatorio_html()
    elif escolha == "6":
            run_pagerank_analysis()
            run_bfs_analysis()
            run_dfs_analysis()
            gerar_relatorio_html()
    elif escolha == "8":  
            run_dfs_analysis()
            gerar_relatorio_html()
    elif escolha == "7":
            console.print()
            exibir_painel(
                "Avançando para a [bold]Etapa 3[/] — Visualizações Avançadas.",
                "Próxima Etapa",
                "blue"
            )
            return "stage3"
    elif escolha == "9":
            console.print()
            exibir_painel(
                "Retornando à [bold]Etapa 1[/] para reconstruir o grafo com outro escopo.",
                "Voltar",
                "yellow"
            )
            return "back"
    else:
            # "0" ou None (Ctrl+C) → encerrar
            return "exit"


def _menu_visualizacoes():
    """
    ETAPA 3 — Visualizações Avançadas.
    Gera gráficos analíticos sobre os grafos já construídos.
    Retorna:
      "back"   → voltar à Etapa 2
      "exit"   → encerrar o programa
    """
    console.print()
    console.rule("[bold blue]ETAPA 3 — Visualizações Avançadas[/]", style="blue")

    while True:
        console.print()
        exibir_painel(_TEXTO_ETAPA3, "Gráficos Analíticos Avançados", "blue")
        escolha = questionary.select(
            "Qual visualização deseja gerar?",
            choices=[
                Choice("1 — Distribuição de Grau   (topologia global da rede)", value="1"),
                Choice("2 — Comparativo Top 10      (relevância BAD/MID/GOOD lado a lado)", value="2"),
                Choice("3 — Heatmap de Coocorrência (combos semânticos entre hubs)", value="3"),
                Choice("4 — Scatter de Deslocamento (palavras que discriminam satisfação)", value="4"),
                Choice("5 — Word Cloud (PageRank)   (impressão visual do vocabulário)", value="5"),
                Choice("6 — Gerar Todas as Visualizações (1 a 5)", value="6"),
                Choice("7 — Voltar — retornar à Etapa 2", value="7"),
                Choice("0 — Sair", value="0"),
            ],
            style=ESTILO,
        ).ask()

        if escolha == "1":
            gerar_distribuicao_grau()
            gerar_relatorio_html()
        elif escolha == "2":
            gerar_comparativo_top10()
            gerar_relatorio_html()
        elif escolha == "3":
            gerar_heatmap_coocorrencia()
            gerar_relatorio_html()
        elif escolha == "4":
            gerar_scatter_deslocamento()
            gerar_relatorio_html()
        elif escolha == "5":
            gerar_wordcloud_pagerank()
            gerar_relatorio_html()
        elif escolha == "6":
            run_todas_visualizacoes()
            gerar_relatorio_html()
        elif escolha == "7":
            console.print()
            exibir_painel(
                "Retornando à [bold]Etapa 2[/] — Análises Adicionais.",
                "Voltar",
                "yellow"
            )
            return "back"
        else:
            # "0" ou None (Ctrl+C) → encerrar
            return "exit"


def run_menu_principal(cleaned_dir, processed_dir, carregar_func, salvar_func):

    while True:
        # ── ETAPA 1: construção dos grafos ──
        grafo_construido = _menu_escopo(cleaned_dir, processed_dir, carregar_func, salvar_func)
        if not grafo_construido:
            despedida()
            break

        # ── ETAPA 2: análises adicionais (loop interno) ──
        while True:
            resultado_e2 = _menu_analises_adicionais()

            if resultado_e2 == "exit":
                despedida()
                return

            if resultado_e2 == "back":
                break  # volta ao início do loop externo (Etapa 1)

            # resultado_e2 == "stage3" → entra na Etapa 3
            while True:
                resultado_e3 = _menu_visualizacoes()

                if resultado_e3 == "exit":
                    despedida()
                    return

                # resultado_e3 == "back" → retorna ao loop da Etapa 2
                break
