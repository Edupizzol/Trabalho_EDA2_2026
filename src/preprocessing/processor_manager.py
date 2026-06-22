import os
import json
import itertools
from collections import Counter
from src.preprocessing.text_cleaner import ReviewPreprocessor


class ProcessManager:
    def __init__(self, input_dir: str, output_dir: str, window_size: int = 3):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.cleaner = ReviewPreprocessor()
        self.window_size = window_size

    def process_all_tiers(self):
        print(f"Iniciando pré-processamento e extração de arestas (Sliding Window size={self.window_size})...")
        os.makedirs(self.output_dir, exist_ok=True)

        target_files = ["bad_reviews.json", "mid_reviews.json", "good_reviews.json"]

        for filename in target_files:
            input_path = os.path.join(self.input_dir, filename)
            output_path = os.path.join(self.output_dir, filename)

            if not os.path.exists(input_path):
                print(f"Arquivo {filename} não encontrado. Pulando...")
                continue

            print(f"Processando e gerando coocorrências para {filename}...")
            with open(input_path, 'r', encoding='utf-8') as f:
                reviews = json.load(f)

            edge_counter = Counter()

            for review in reviews:
                tokens = self.cleaner.clean_text(review)

                if len(tokens) < 2:
                    continue

                # Percorre o texto aplicando a Janela Deslizante
                for i in range(len(tokens)):
                    # Captura o bloco atual de palavras dentro do tamanho da janela
                    window = tokens[i: i + self.window_size]

                    # Remove duplicatas dentro da mesma janela para evitar self-loops (palavra ligando a ela mesma)
                    unique_window = list(set(window))
                    if len(unique_window) < 2:
                        continue

                    # Gera todas as combinações de 2 a 2 entre os elementos desta janela
                    for word1, word2 in itertools.combinations(unique_window, 2):
                        # Ordena em ordem alfabética para garantir que o Grafo seja Não-Direcionado
                        # Ex: ("bateria", "ruim") e ("ruim", "bateria") contarão juntos na mesma chave
                        pair = tuple(sorted([word1, word2]))
                        edge_counter[pair] += 1

            # Transforma o Counter de arestas no formato JSON esperado pelo contrato da Issue
            edges_list = [
                {
                    "source": pair[0],
                    "target": pair[1],
                    "weight": weight
                }
                for pair, weight in edge_counter.items()
            ]

            # Salva o arquivo JSON com a lista de arestas pesadas
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(edges_list, f, ensure_ascii=False, indent=4)

            print(f"Salvo: {len(edges_list)} arestas únicas calculadas em {output_path}")