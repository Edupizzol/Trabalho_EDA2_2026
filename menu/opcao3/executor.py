import os
from menu.common import pipeline_grafos_e_visualizacao
from src.interface.console import log_info, log_aviso

def executar_opcao_3(cleaned_dir, processed_dir):
    """
    Executa a pipeline de grafos utilizando 100% dos dados disponíveis,
    sem sub-amostragem, e gera os relatórios consolidados na pasta da Opção 3.
    """
    log_info("Iniciando processamento do escopo TOTAL de dados...")
    log_aviso("Esta operação analisa o dataset completo e pode levar mais tempo.")

    output_opcao_dir = "outputs/menu/opcao3"

    # Dispara a função coringa passando o diretório original completo (cleaned_dir)
    pipeline_grafos_e_visualizacao(
        input_amostra_dir=cleaned_dir,  # <--- Aqui entra o escopo total direto!
        processed_dir=processed_dir,
        output_opcao_dir=output_opcao_dir,
        titulo_md="Relatório Executivo - Escopo Total do Dataset",
        subtitulo_md="Resultados consolidados considerando 100% das reviews tratadas pela pipeline."
    )
    return True