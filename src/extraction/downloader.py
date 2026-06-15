import os
from kaggle.api.kaggle_api_extended import KaggleApi

class KaggleDatasetDownloader:
    def __init__(self, dataset_slug: str, output_dir: str):
        self.dataset_slug = dataset_slug
        self.output_dir = output_dir
        self.api = KaggleApi()
        self.api.authenticate()

    def fetch_data(self):
        print(f"Buscando dataset '{self.dataset_slug}' via Kaggle API...")
        os.makedirs(self.output_dir, exist_ok=True)
        self.api.dataset_download_files(self.dataset_slug, path=self.output_dir, unzip=True)
        print(f"Dataset extraído com sucesso em: {self.output_dir}/")