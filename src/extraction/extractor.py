import os
import json
import pandas as pd

class ReviewExtractor:
    def __init__(self, raw_data_path: str, output_dir: str):
        self.raw_data_path = raw_data_path
        self.output_dir = output_dir

    def run(self):
        print("Iniciando segregação dos dados do B2W...")

        df = pd.read_csv(self.raw_data_path, sep=';', usecols=['rating', 'review_text'])
        df = df.dropna(subset=['rating', 'review_text'])

        # AJUSTE 3: Atualizar referências para bater com as colunas minúsculas do DataFrame
        bad_reviews = df[df['rating'].isin([1, 2])]['review_text'].tolist()
        mid_reviews = df[df['rating'] == 3]['review_text'].tolist()
        good_reviews = df[df['rating'].isin([4, 5])]['review_text'].tolist()

        os.makedirs(self.output_dir, exist_ok=True)

        datasets = {
            "bad_reviews.json": bad_reviews,
            "mid_reviews.json": mid_reviews,
            "good_reviews.json": good_reviews
        }

        for filename, data in datasets.items():
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Salvo: {len(data)} reviews em {filepath}")