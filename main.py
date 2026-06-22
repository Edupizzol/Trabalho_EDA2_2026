import os
import json

from src.extraction.downloader import KaggleDatasetDownloader
from src.extraction.extractor import ReviewExtractor
from src.interface.console import exibir_banner, exibir_fase
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

    # Ingestão e Segregação rápidas
    exibir_fase(1, "INGESTÃO DE DADOS (API)")
    downloader = KaggleDatasetDownloader(dataset_slug=KAGGLE_DATASET, output_dir=RAW_DIR)
    downloader.fetch_data()

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
