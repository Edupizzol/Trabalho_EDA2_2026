# src/extraction/extractor.py
import os
import json
import pandas as pd

class ReviewExtractor:
    def __init__(self, raw_data_path: str, output_dir: str):
        self.raw_data_path = raw_data_path
        self.output_dir = output_dir

    def run(self):
        print("Iniciando segregação dos dados...")
        
        # Ajustado para as colunas do novo dataset público
        df = pd.read_csv(self.raw_data_path, usecols=['Rating', 'ReviewText'])
        df = df.dropna(subset=['Rating', 'ReviewText'])

        # Divide as categorias por estrelas
        bad_reviews = df[df['Rating'].isin([1, 2])]['ReviewText'].tolist()
        mid_reviews = df[df['Rating'] == 3]['ReviewText'].tolist()
        good_reviews = df[df['Rating'].isin([4, 5])]['ReviewText'].tolist()

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