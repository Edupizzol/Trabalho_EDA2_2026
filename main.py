import os
import json

from src.extraction.extractor import ReviewExtractor
from src.interface.console import exibir_banner, exibir_fase, log_info, log_ok, log_erro
from src.interface.menus import run_menu_principal


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


def main():
    KAGGLE_DATASET = "fredericods/ptbr-sentiment-analysis-datasets"
    RAW_DIR = "data/raw"
    CLEANED_DIR = "data/cleaned"
    PROCESSED_DIR = "data/processed"
    RAW_CSV_PATH = f"{RAW_DIR}/b2w.csv"

    exibir_banner()

    # Verifica se os arquivos de texto segregados já existem
    categorias = ["bad_reviews", "mid_reviews", "good_reviews"]
    arquivos_limpos_existem = all(
        os.path.exists(os.path.join(CLEANED_DIR, f"{cat}.json"))
        for cat in categorias
    )

    if arquivos_limpos_existem:
        log_ok("Arquivos limpos detectados em 'data/cleaned/'. Pula Ingestão (API).")
    else:
        # Tenta ingestão se o CSV bruto não estiver local
        if not os.path.exists(RAW_CSV_PATH):
            exibir_fase(1, "INGESTÃO DE DADOS (API)")
            
            # Verifica se as credenciais do Kaggle estão presentes
            home_dir = os.path.expanduser("~")
            kaggle_config_path = os.path.join(home_dir, ".kaggle", "kaggle.json")
            has_kaggle_env = "KAGGLE_USERNAME" in os.environ and "KAGGLE_KEY" in os.environ
            has_kaggle_file = os.path.exists(kaggle_config_path)

            if has_kaggle_env or has_kaggle_file:
                try:
                    from src.extraction.downloader import KaggleDatasetDownloader
                    downloader = KaggleDatasetDownloader(dataset_slug=KAGGLE_DATASET, output_dir=RAW_DIR)
                    downloader.fetch_data()
                except BaseException as e:
                    print(f"\n  [ AVISO ] Falha ao tentar baixar via Kaggle API: {e}")
            else:
                print("\n  [ AVISO ] Credenciais do Kaggle não encontradas (~/.kaggle/kaggle.json ou variáveis de ambiente).")
                print("  Se você quiser atualizar a base de dados, configure sua API Key no Kaggle.")
                print("  Como o download automático não é possível, tentaremos prosseguir com os dados locais.\n")
                
                # Se os grafos já existirem, prossegue; caso contrário, encerra
                grafos_existem = all(
                    os.path.exists(f"data/graphs/{cat}_graph.json") for cat in categorias
                )
                if grafos_existem:
                    log_info("Grafos prontos localizados em 'data/graphs/'. Você poderá rodar as Etapas 2 e 3.")
                else:
                    log_erro("Nenhum dado limpo ou grafo pré-existente encontrado. Abortando.")
                    return

        # Executa a segregação se o CSV estiver disponível
        if os.path.exists(RAW_CSV_PATH):
            exibir_fase(2, "SEGREGAÇÃO DE TEXTO")
            extractor = ReviewExtractor(raw_data_path=RAW_CSV_PATH, output_dir=CLEANED_DIR)
            extractor.run()

    # Toda a interação com o usuário (menus, escolhas, navegação) vive na
    # camada `interface/`. O main apenas injeta os callbacks de dados.
    run_menu_principal(
        cleaned_dir=CLEANED_DIR,
        processed_dir=PROCESSED_DIR,
        carregar_func=carregar_reviews_limpas,
        salvar_func=salvar_reviews_amostradas,
    )


if __name__ == "__main__":
    main()
