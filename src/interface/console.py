
import sys

from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text

# No Windows o stdout pode usar cp1252 por padrão, que não codifica vários
# caracteres Unicode (setas, bordas) usados pelo Rich. Forçamos UTF-8 para
# evitar UnicodeEncodeError e melhorar o desenho dos painéis.
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Instância única compartilhada por toda a aplicação.
console = Console()

# Cor dos textos de log — cinza escuro consistente em toda a aplicação.
_COR_LOG = "color(244)"


# ── Componentes visuais principais ──────────────────────────────────────────

def exibir_banner():
    """Mostra o banner de abertura da aplicação."""
    titulo = Text("ANÁLISE DE UTILIDADE EM REVIEWS", justify="center", style="bold cyan")
    subtitulo = Text(
        "Grafos de Coocorrência de Palavras  •  EDA II",
        justify="center",
        style="dim",
    )
    console.print()
    console.print(
        Panel(
            Group(titulo, subtitulo),
            border_style="cyan",
            padding=(1, 4),
        )
    )


def exibir_fase(numero: int, titulo: str):
    """Cabeçalho de uma fase do pipeline (ex.: ingestão, segregação)."""
    console.print()
    console.rule(f"[bold blue]FASE {numero} — {titulo}", style="blue")


def exibir_secao(titulo: str):
    """Separador interno de seção dentro de uma fase."""
    console.print()
    console.rule(f"[bold]{titulo}[/]", style="dim")


def exibir_painel(conteudo: str, titulo: str, cor: str = "cyan"):
    """Exibe um painel explicativo com borda colorida e título."""
    console.print(
        Panel(
            conteudo,
            title=f"[bold]{titulo}[/]",
            border_style=cor,
            padding=(1, 2),
        )
    )


def despedida():
    """Mensagem de encerramento da aplicação."""
    console.print()
    console.print("[dim]Encerrando. Até a próxima![/]")


# ── Funções de log padronizadas ──────────────────────────────────────────────

def log_info(msg: str):
    """Progresso e etapas informativas."""
    console.print(f"  [dim white]\\[INFO][/]  [{_COR_LOG}]{msg}[/]")


def log_ok(msg: str):
    """Operação concluída com sucesso."""
    console.print(f"  [bold green]\\[ OK ][/]  [{_COR_LOG}]{msg}[/]")


def log_erro(msg: str):
    """Erro ou falha."""
    console.print(f"  [bold red]\\[ERRO][/]  [{_COR_LOG}]{msg}[/]")


def log_aviso(msg: str):
    """Aviso ou situação não ideal."""
    console.print(f"  [bold yellow]\\[AVIS][/]  [{_COR_LOG}]{msg}[/]")


def log_dados(msg: str):
    """Métrica ou dado gerado."""
    console.print(f"  [dim cyan]\\[DADO][/]  [{_COR_LOG}]{msg}[/]")


# ── Aliases legados (usados por menus.py) ────────────────────────────────────

def sucesso(msg: str):
    log_ok(msg)

def erro(msg: str):
    log_erro(msg)

def aviso(msg: str):
    log_aviso(msg)

def info(msg: str):
    log_info(msg)
