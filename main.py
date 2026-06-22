import os
import json
import random
from src.extraction.downloader import KaggleDatasetDownloader
from src.extraction.extractor import ReviewExtractor
from src.preprocessing.processor_manager import ProcessManager
from src.graph_construction.graph_builder import build_graphs_from_categories
from src.analysis.bfs import run_bfs_analysis

# Importa a execução do PageRank diretamente da estrutura de pastas do seu src
from src.analysis.pagerank_runner import run_pagerank_analysis


def carregar_reviews_limpas(cleaned_dir):
    """Carrega as reviews segregadas da Fase 2 para permitir a amostragem/seleção"""
    categorias = ["bad_reviews", "mid_reviews", "good_reviews"]
    dados = {}
    for cat in categorias:
        caminho = os.path.join(cleaned_dir, f"{cat}.json")
        if os.path.exists(caminho):
            with open(caminho, 'r', encoding='utf-8') as f:
                dados[cat] = json.load(f)
        else:
            dados[cat] = []
    return dados


def salvar_reviews_amostradas(processed_dir, dados_amostrados):
    """Salva a amostra temporária de texto limpo"""
    os.makedirs(processed_dir, exist_ok=True)
    for cat, reviews in dados_amostrados.items():
        caminho = os.path.join(processed_dir, f"{cat}.json")
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=4)


def menu_interativo(cleaned_dir, processed_dir):
    print("\n==================================================")
    print("         MENU DE CONFIGURAÇÃO DO ESCOPO           ")
    print("==================================================")
    print("1 - Amostragem Rápida: Pegar 100 reviews de cada e montar grafo")
    print("2 - Seleção Manual: Escolher quais reviews entram no grafo")
    print("3 - Escopo Total: Processar TODAS as reviews (Demorado)")
    print("4 - Executar Análise de PageRank nos grafos construídos")
    print("5 - Executar Análise de Vizinhança Semântica via BFS")
    print("0 - Sair")
    opcao = input("\nEscolha uma opção: ")

    if opcao == "1":
        dados = carregar_reviews_limpas(cleaned_dir)
        if not any(dados.values()):
            print("[!] Erro: Rode a pipeline completa primeiro.")
            return False

        print("\n[+] Gerando amostra aleatória de 100 reviews por categoria...")
        dados_amostrados = {}
        for cat, lista in dados.items():
            dados_amostrados[cat] = random.sample(lista, min(len(lista), 100))
            print(f" -> {cat}: 100 reviews selecionadas.")

        salvar_reviews_amostradas(cleaned_dir + "_amostra", dados_amostrados)
        print("[+] Rodando pré-processamento rápido (Sliding Window)...")
        processor = ProcessManager(input_dir=cleaned_dir + "_amostra", output_dir=processed_dir)
        processor.process_all_tiers()

        print("\n--- FASE 4: CONSTRUÇÃO DOS GRAFOS ---")
        categorias = ["bad_reviews", "mid_reviews", "good_reviews"]
        build_graphs_from_categories(processed_dir, categorias)
        return True

    elif opcao == "2":
        dados = carregar_reviews_limpas(cleaned_dir)
        dados_selecionados = {"bad_reviews": [], "mid_reviews": [], "good_reviews": []}
        for cat, lista in dados.items():
            print(f"\n--- Seleção para a categoria: {cat} ---")
            amostra_visualizacao = random.sample(lista, min(len(lista), 5))

            for idx, review in enumerate(amostra_visualizacao, 1):
                print(f"\n[{idx}] {review[:200]}...")
                escolha = input(f"Deseja incluir essa review? (s/n): ").lower()
                if escolha == 's':
                    dados_selecionados[cat].append(review)

            if not dados_selecionados[cat]:
                dados_selecionados[cat].append(random.choice(lista))

        salvar_reviews_amostradas(cleaned_dir + "_amostra", dados_selecionados)
        processor = ProcessManager(input_dir=cleaned_dir + "_amostra", output_dir=processed_dir)
        processor.process_all_tiers()

        print("\n--- FASE 4: CONSTRUÇÃO DOS GRAFOS ---")
        categorias = ["bad_reviews", "mid_reviews", "good_reviews"]
        build_graphs_from_categories(processed_dir, categorias)
        return True

    elif opcao == "3":
        print("\n[+] Processando o escopo total de dados...")
        processor = ProcessManager(input_dir=cleaned_dir, output_dir=processed_dir)
        processor.process_all_tiers()

        print("\n--- FASE 4: CONSTRUÇÃO DOS GRAFOS ---")
        categorias = ["bad_reviews", "mid_reviews", "good_reviews"]
        build_graphs_from_categories(processed_dir, categorias)
        return True

    elif opcao == "4":
        # Dispara diretamente o script analítico da outra dupla
        run_pagerank_analysis()
        return False

    elif opcao == "5":
        run_bfs_analysis()
        return False

    else:
        print("\n[-] Saindo...")
        return False


def main():
    KAGGLE_DATASET = "fredericods/ptbr-sentiment-analysis-datasets"
    RAW_DIR = "data/raw"
    CLEANED_DIR = "data/cleaned"
    PROCESSED_DIR = "data/processed"
    RAW_CSV_PATH = f"{RAW_DIR}/b2w.csv"

    # Ingestão e Segregação rápidas
    print("--- FASE 1: INGESTÃO DE DADOS (API) ---")
    downloader = KaggleDatasetDownloader(dataset_slug=KAGGLE_DATASET, output_dir=RAW_DIR)
    downloader.fetch_data()

    print("\n--- FASE 2: SEGREGAÇÃO DE TEXTO ---")
    extractor = ReviewExtractor(raw_data_path=RAW_CSV_PATH, output_dir=CLEANED_DIR)
    extractor.run()

    # Menu controla as fases pesadas e analíticas
    menu_interativo(CLEANED_DIR, PROCESSED_DIR)


if __name__ == "__main__":
    main()