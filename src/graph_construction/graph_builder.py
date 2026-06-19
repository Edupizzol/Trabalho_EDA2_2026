import json

class GraphBuilder:
    def __init__(self):
        self.graph = {}
        self.id_to_word=[]
        self.word_to_id={}

    def get_or_create_word(self, word):
        if word not in self.word_to_id:
            self.word_to_id[word] = len(self.id_to_word)
            self.id_to_word.append(word)
            self.graph[self.word_to_id[word]] = {}
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

    def add_review(self, words):
        for i in range(len(words)):
            for j in range(i+1, len(words)):
                self.add_edge(words[i], words[j])

    def build_graph(self, documents):
        for words in documents:
            self.add_review(words)

    def get_graph(self):
        return self.graph

    def get_word_to_id(self):
        return self.word_to_id

    def get_id_to_word(self):
        return self.id_to_word

    def save_graph(self, filename):
        pass

    # que dados vamos coletar? pq ja tem o page rank
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


def build_graphs_from_categories(processed_dir, categorias):

    builders = {}

    for categoria in categorias:
        caminho = f"{processed_dir}/{categoria}.json"
        with open(caminho, 'r', encoding='utf-8') as f:
            documentos = json.load(f)

        builder = GraphBuilder()
        builder.build_graph(documentos)
        builders[categoria] = builder

        total_vertices = len(builder.get_id_to_word())
        total_arestas = sum(len(v) for v in builder.get_graph().values()) // 2
        print(f"{categoria}: {total_vertices} vértices, {total_arestas} arestas")

    return builders