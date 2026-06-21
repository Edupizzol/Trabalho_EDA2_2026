from src.extraction.downloader import KaggleDatasetDownloader
from src.extraction.extractor import ReviewExtractor
from src.preprocessing.processor_manager import ProcessManager

def main():
    KAGGLE_DATASET = "luisfredgs/b2w-reviews01"

    RAW_DIR = "data/raw"
    CLEANED_DIR = "data/cleaned"
    PROCESSED_DIR = "data/processed"

    # AJUSTE 2: Nome real do arquivo CSV extraído do dataset B2W
    RAW_CSV_PATH = f"{RAW_DIR}/B2W-Reviews01.csv"

    print("--- FASE 1: INGESTÃO DE DADOS (API) ---")
    downloader = KaggleDatasetDownloader(dataset_slug=KAGGLE_DATASET, output_dir=RAW_DIR)
    downloader.fetch_data()

    print("\n--- FASE 2: SEGREGAÇÃO DE TEXTO ---")
    extractor = ReviewExtractor(raw_data_path=RAW_CSV_PATH, output_dir=CLEANED_DIR)
    extractor.run()

    print("\n--- FASE 3: PRÉ-PROCESSAMENTO DE TEXTO ---")
    processor = ProcessManager(input_dir=CLEANED_DIR, output_dir=PROCESSED_DIR)
    processor.process_all_tiers()


if __name__ == "__main__":
    main()