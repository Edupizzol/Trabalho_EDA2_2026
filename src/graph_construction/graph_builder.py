import json
import sys
sys.setrecursionlimit(50000)

class GraphBuilder:
    def __init__(self):
        self.graph = {}
        self.id_to_word = []
        self.word_to_id = {}

    def get_or_create_word(self, word):
        if word not in self.word_to_id:
            word_id = len(self.id_to_word)
            self.word_to_id[word] = word_id
            self.id_to_word.append(word)
            self.graph[word_id] = {}
        return self.word_to_id[word]

    def add_edge(self, word1, word2):
        id1 = self.get_or_create_word(word1)
        id2 = self.get_or_create_word(word2)
        if id1 not in self.graph[id2]:
            self.graph[id2][id1] = 0
        if id2 not in self.graph[id1]:
            self.graph[id1][id2] = 0

        self.graph[id2][id1] += 1
        self.graph[id1][id2] += 1

    def add_review(self, words_list):
        words = list(set(words_list))
        for i in range(len(words)):
            for j in range(i+1, len(words)):
                if words[i] == words[j]:
                    continue
                self.add_edge(words[i], words[j])

    def add_calculated_edge(self, word1, word2, weight):
        id1 = self.get_or_create_word(word1)
        id2 = self.get_or_create_word(word2)

        # Força o weight a ser um inteiro para evitar o TypeError
        weight_int = int(weight)

        # Acessa com segurança e soma os inteiros
        self.graph[id1][id2] = self.graph[id1].get(id2, 0) + weight_int
        self.graph[id2][id1] = self.graph[id2].get(id1, 0) + weight_int

    def build_graph(self, edges_list):
        for edge in edges_list:
            if isinstance(edge, dict):
                # Altere as chaves abaixo se o seu JSON usar nomes diferentes (ex: 'source', 'target', 'cooccurrence')
                w1 = edge.get("word1") or edge.get("source")
                w2 = edge.get("word2") or edge.get("target")
                weight = edge.get("weight") or edge.get("cooccurrence") or 1

                if w1 and w2:
                    self.add_calculated_edge(w1, w2, weight)

            #Caso ainda venha como uma lista pura 
            elif isinstance(edge, (list, tuple)):
                if len(edge) == 3:
                    w1, w2, weight = edge
                    self.add_calculated_edge(w1, w2, weight)
                elif len(edge) == 2:
                    w1, w2 = edge
                    self.add_calculated_edge(w1, w2, 1)

    def get_graph(self):
        return self.graph

    def get_word_to_id(self):
        return self.word_to_id

    def get_id_to_word(self):
        return self.id_to_word

    def save_graph(self, filename):
        data = {
            "grafo": {
                "graph": self.graph,
                "id_to_word": self.id_to_word,
                "word_to_id": self.word_to_id,
            },
            "dados": {
                "total_vertices": len(self.id_to_word),
                "total_arestas": sum(len(v) for v in self.graph.values()) // 2,
                "numero_componentes": len(self.componentes_conectados()),
                "componentes_conectados": self.componentes_conectados(),
                "graus": [self.degree(word) for word in self.id_to_word],
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def bfs(self, start_word):
        if start_word not in self.word_to_id:
            return []
        start_id = self.word_to_id[start_word]
        visitados = set()
        fila = [start_id]
        visitados.add(start_id)
        ordem_visita = []

        while fila:
            atual = fila.pop(0)
            ordem_visita.append(atual)
            for vizinho_id in self.graph[atual]:
                if vizinho_id not in visitados:
                    visitados.add(vizinho_id)
                    fila.append(vizinho_id)

        return [self.id_to_word[i] for i in ordem_visita]

    def degree(self, word):
        if word not in self.word_to_id:
            return 0
        return len(self.graph[self.word_to_id[word]])

    def dfs(self, vertice_id, visitados, componente):
        visitados.add(vertice_id)
        componente.append(vertice_id)
        for vizinho_id in self.graph[vertice_id]:
            if vizinho_id not in visitados:
                self.dfs(vizinho_id, visitados, componente)

    def componentes_conectados(self):
        visitados = set()
        componentes = []
        for vertice_id in self.graph:
            if vertice_id not in visitados:
                componente = []
                self.dfs(vertice_id, visitados, componente)
                componente_word = [self.id_to_word[i] for i in componente]
                componentes.append(componente_word)
        return componentes

def build_graphs_from_categories(processed_dir, categorias):
    import os
    builders = {}
    os.makedirs("data/graphs", exist_ok=True)

    for categoria in categorias:
        caminho = f"{processed_dir}/{categoria}.json"
        with open(caminho, 'r', encoding='utf-8') as f:
            edges_list = json.load(f)

        builder = GraphBuilder()
        builder.build_graph(edges_list)
        builders[categoria] = builder

        total_vertices = len(builder.get_id_to_word())
        total_arestas = sum(len(v) for v in builder.get_graph().values()) // 2
        print(f"{categoria}: {total_vertices} vértices, {total_arestas} arestas")

        builder.save_graph(f"data/graphs/{categoria}_graph.json")

    return builders