import os
import json
from src.preprocessing.text_cleaner import ReviewPreprocessor

class ProcessManager:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.cleaner = ReviewPreprocessor()

    def process_all_tiers(self):
        print("Iniciando o pré-processamento de texto com spaCy...")
        os.makedirs(self.output_dir, exist_ok=True)

        target_files = ["bad_reviews.json", "mid_reviews.json", "good_reviews.json"]

        for filename in target_files:
            input_path = os.path.join(self.input_dir, filename)
            output_path = os.path.join(self.output_dir, filename)

            if not os.path.exists(input_path):
                print(f"Arquivo {filename} não encontrado. Pulando...")
                continue

            print(f"Processando {filename}...")
            with open(input_path, 'r', encoding='utf-8') as f:
                reviews = json.load(f)

            processed_reviews = []
            for review in reviews:
                tokens = self.cleaner.clean_text(review)
                if tokens: 
                    processed_reviews.append(tokens)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_reviews, f, ensure_ascii=False, indent=4)
            
            print(f"Salvo: {len(processed_reviews)} reviews limpas em {output_path}")