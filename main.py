# main.py
from src.extraction.downloader import KaggleDatasetDownloader
from src.extraction.extractor import ReviewExtractor

def main():
    # NOVO DATASET ATIVO:
    KAGGLE_DATASET = "muhammadzamin1/product-reviews-dataset-for-sentiment-analysis"
    RAW_DIR = "data/raw"
    CLEANED_DIR = "data/cleaned"
    
    # O CSV que vem dentro desse novo zip se chama 'product_reviews.csv'
    RAW_CSV_PATH = f"{RAW_DIR}/product_reviews_mock_data.csv"

    print("--- FASE 1: INGESTÃO DE DADOS (API) ---")
    downloader = KaggleDatasetDownloader(dataset_slug=KAGGLE_DATASET, output_dir=RAW_DIR)
    downloader.fetch_data()

    print("\n--- FASE 2: SEGREGAÇÃO DE TEXTO ---")
    extractor = ReviewExtractor(raw_data_path=RAW_CSV_PATH, output_dir=CLEANED_DIR)
    extractor.run()

if __name__ == "__main__":
    main()