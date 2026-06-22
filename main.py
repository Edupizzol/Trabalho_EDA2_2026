import os
import json
import random
from src.extraction.downloader import KaggleDatasetDownloader
from src.extraction.extractor import ReviewExtractor
from src.preprocessing.processor_manager import ProcessManager
from src.graph_construction.graph_builder import build_graphs_from_categories


def carregar_reviews_limpas(cleaned_dir):
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
    os.makedirs(processed_dir, exist_ok=True)
    for cat, reviews in dados_amostrados.items():
        caminho = os.path.join(processed_dir, f"{cat}.json")
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, ensure_ascii=False, indent=4)


def menu_interativo(cleaned_dir, processed_dir):
    dados = carregar_reviews_limpas(cleaned_dir)
    if not any(dados.values()):
        print("[!] Erro: Nenhum dado encontrado na Fase 2. Rode a pipeline completa primeiro.")
        return False

    print("\n==================================================")
    print("         MENU DE CONFIGURAÇÃO DO ESCOPO           ")
    print("==================================================")
    print("1 - Amostragem Rápida: Pegar 100 reviews aleatórias de cada categoria")
    print("2 - Seleção Manual: Visualizar reviews aleatórias e escolher")
    print("3 - Escopo Total: Processar TODAS as reviews (Cuidado: Fase 3 demorada)")
    print("0 - Sair")
    opcao = input("\nEscolha uma opção: ")

    if opcao == "1":
        print("\n[+] Gerando amostra aleatória de 100 reviews por categoria...")
        dados_amostrados = {}
        for cat, lista in dados.items():
            # Usa o min() caso a lista tenha menos de 100 elementos por algum motivo
            dados_amostrados[cat] = random.sample(lista, min(len(lista), 100))
            print(f" -> {cat}: 100 reviews selecionadas.")

        salvar_reviews_amostradas(cleaned_dir + "_amostra", dados_amostrados)
        print("[+] Rodando pré-processamento rápido (Sliding Window) nas 100 reviews...")
        processor = ProcessManager(input_dir=cleaned_dir + "_amostra", output_dir=processed_dir)
        processor.process_all_tiers()
        return True

    elif opcao == "2":
        dados_selecionados = {"bad_reviews": [], "mid_reviews": [], "good_reviews": []}
        for cat, lista in dados.items():
            print(f"\n--- Seleção para a categoria: {cat} ---")
            amostra_visualizacao = random.sample(lista, min(len(lista), 5))

            for idx, review in enumerate(amostra_visualizacao, 1):
                print(f"\n[{idx}] {review[:200]}...")  # Mostra os primeiros 200 caracteres
                escolha = input(f"Deseja incluir essa review no grafo de {cat}? (s/n): ").lower()
                if escolha == 's':
                    dados_selecionados[cat].append(review)

            if not dados_selecionados[cat]:
                dados_selecionados[cat].append(random.choice(lista))
                print(" -> Nenhuma review escolhida. Adicionada 1 review aleatória por segurança.")

            print(f" -> Total de reviews selecionadas para {cat}: {len(dados_selecionados[cat])}")

        salvar_reviews_amostradas(cleaned_dir + "_amostra", dados_selecionados)
        print("[+] Rodando pré-processamento rápido (Sliding Window) nas reviews escolhidas...")
        processor = ProcessManager(input_dir=cleaned_dir + "_amostra", output_dir=processed_dir)
        processor.process_all_tiers()
        return True

    elif opcao == "3":
        print("\n[+] Processando o escopo total de dados...")
        processor = ProcessManager(input_dir=cleaned_dir, output_dir=processed_dir)
        processor.process_all_tiers()
        return True

    else:
        print("\n[-] Saindo ou opção inválida.")
        return False


def main():
    KAGGLE_DATASET = "fredericods/ptbr-sentiment-analysis-datasets"
    RAW_DIR = "data/raw"
    CLEANED_DIR = "data/cleaned"
    PROCESSED_DIR = "data/processed"
    RAW_CSV_PATH = f"{RAW_DIR}/b2w.csv"

    # Ingestão e Segregação iniciais (Sempre rápidas se o arquivo já existir)
    print("--- FASE 1: INGESTÃO DE DADOS (API) ---")
    downloader = KaggleDatasetDownloader(dataset_slug=KAGGLE_DATASET, output_dir=RAW_DIR)
    downloader.fetch_data()

    print("\n--- FASE 2: SEGREGAÇÃO DE TEXTO ---")
    extractor = ReviewExtractor(raw_data_path=RAW_CSV_PATH, output_dir=CLEANED_DIR)
    extractor.run()

    # Chama o Menu Interativo para controlar as Fases 3 e 4
    deve_construir_grafo = menu_interativo(CLEANED_DIR, PROCESSED_DIR)

    if deve_construir_grafo:
        print("\n--- FASE 4: CONSTRUÇÃO DOS GRAFOS ---")
        categorias = ["bad_reviews", "mid_reviews", "good_reviews"]
        build_graphs_from_categories(PROCESSED_DIR, categorias)


    print("\n--- FASE 5: CÁLCULO DE PAGERANK (ANÁLISE DE REDES) ---")
    from src.analysis.pagerank_runner import run_pagerank_analysis
    run_pagerank_analysis()

if __name__ == "__main__":
    main()