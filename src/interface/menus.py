

import questionary
from questionary import Choice, Style

from src.interface.console import console, exibir_painel, despedida

# Ações disparadas pelos menus.
from menu.opcao1.executor import executar_opcao_1
from menu.opcao2.executor import executar_opcao_2
from menu.opcao3.executor import executar_opcao_3
from src.analysis.pagerank_runner import run_pagerank_analysis
from src.analysis.bfs import run_bfs_analysis


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
    "  [dim]\"Em que contexto uma palavra aparece em cada nível?\"[/]"
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

    if escolha == "1":
        executar_opcao_1(cleaned_dir, processed_dir, carregar_func, salvar_func)
        return True
    elif escolha == "2":
        executar_opcao_2(cleaned_dir, processed_dir, carregar_func, salvar_func)
        return True
    elif escolha == "3":
        executar_opcao_3(cleaned_dir, processed_dir)
        return True
    else:
        # "0" ou None (Ctrl+C) → encerrar
        return False


def _menu_analises_adicionais():
    """
    ETAPA 2 — Análises Adicionais.
    Roda análises sobre os grafos já construídos na Etapa 1. Fica em loop
    até o usuário voltar ou sair.
    Retorna True para voltar à Etapa 1 (reconstruir), False para encerrar.
    """
    console.print()
    console.rule("[bold magenta]ETAPA 2 — Análises Adicionais[/]", style="magenta")

    while True:

        console.print()
        exibir_painel(_TEXTO_ETAPA2, "Opções de Análises Adicionais", "magenta")
        escolha = questionary.select(
            "O que deseja executar sobre os grafos construídos?",
            choices=[
                Choice("PageRank — palavras mais centrais (tabela comparativa Top 15)", value="4"),
                Choice("BFS Contextual — vizinhança semântica de palavras-chave", value="5"),
                Choice("Execute Todas As Análises Adicionais (PageRank e BFS Contextual)", value="6"),
                Choice("Voltar — reconstruir o grafo com outro escopo", value="9"),
                Choice("Sair", value="0"),
            ],
            style=ESTILO,
        ).ask()

        if escolha == "4":
            run_pagerank_analysis()
        elif escolha == "5":
            run_bfs_analysis()
        elif escolha == "6":
            run_pagerank_analysis()
            run_bfs_analysis()
        elif escolha == "9":
            console.print()
            exibir_painel(
                "Retornando à [bold]Etapa 1[/] para reconstruir o grafo com outro escopo.",
                "Voltar",
                "yellow"
            )
            return True
        else:
            # "0" ou None (Ctrl+C) → encerrar
            return False


def run_menu_principal(cleaned_dir, processed_dir, carregar_func, salvar_func):

    while True:
        grafo_construido = _menu_escopo(cleaned_dir, processed_dir, carregar_func, salvar_func)
        if not grafo_construido:
            despedida()
            break

        voltar_ao_escopo = _menu_analises_adicionais()
        if not voltar_ao_escopo:
            despedida()
            break
