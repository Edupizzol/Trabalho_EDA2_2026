import os
import random
from menu.common import pipeline_grafos_e_visualizacao

def executar_opcao_1(cleaned_dir, processed_dir, carregar_func, salvar_func):
    dados = carregar_func(cleaned_dir)
    if not any(dados.values()):
        print("[!] Erro: Dados base não encontrados.")
        return False

    output_opcao_dir = "outputs/menu/opcao1"
    os.makedirs(output_opcao_dir, exist_ok=True)

    print("\n[+] [Opção 1] Gerando amostra aleatória de 100 reviews por categoria...")
    dados_amostrados = {}
    categorias = ["bad_reviews", "mid_reviews", "good_reviews"]

    for cat in categorias:
        lista = dados.get(cat, [])
        dados_amostrados[cat] = random.sample(lista, min(len(lista), 100))
        print(f" -> {cat}: 100 reviews selecionadas.")

    input_amostra_dir = cleaned_dir + "_amostra"
    salvar_func(input_amostra_dir, dados_amostrados)

    # Invoca a função coringa
    pipeline_grafos_e_visualizacao(
        input_amostra_dir=input_amostra_dir,
        processed_dir=processed_dir,
        output_opcao_dir=output_opcao_dir,
        titulo_md="Relatório Executivo - Amostragem Célula (100 Reviews)",
        subtitulo_md="Resultados calculados sobre uma janela restrita de amostragem automática."
    )
    return True