class MinHeap:
    """
    Uma estrutura de dados Min-Heap personalizada para manter os top-K elementos.
    Armazena tuplas no formato (score, item) e ordena com base no score.
    """
    def __init__(self, max_size: int):
        self.heap = []
        self.max_size = max_size

    def push(self, element: tuple):
        """
        Adiciona um elemento ao heap. Se ultrapassar o tamanho máximo,
        mantém apenas os maiores elementos removendo o menor (a raiz do min-heap).
        """
        if len(self.heap) < self.max_size:
            self.heap.append(element)
            self._upheap(len(self.heap) - 1)
        elif element[0] > self.heap[0][0]:
            self.heap[0] = element
            self._downheap(0)

    def _upheap(self, idx: int):
        parent = (idx - 1) // 2
        while idx > 0 and self.heap[idx][0] < self.heap[parent][0]:
            self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
            idx = parent
            parent = (idx - 1) // 2

    def _downheap(self, idx: int):
        n = len(self.heap)
        left = 2 * idx + 1
        while left < n:
            smallest = idx
            if self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            right = left + 1
            if right < n and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right
            if smallest == idx:
                break
            self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
            idx = smallest
            left = 2 * idx + 1

    def get_sorted(self) -> list:
        """
        Retorna todos os elementos do heap ordenados de forma decrescente (do maior para o menor score).
        Este método não esvazia permanentemente o heap original.
        """
        temp_heap = list(self.heap)
        sorted_elements = []
        
        while temp_heap:
            if len(temp_heap) == 1:
                val = temp_heap.pop()
            else:
                val = temp_heap[0]
                temp_heap[0] = temp_heap.pop()
                # Ajusta o heap (downheap)
                idx = 0
                n = len(temp_heap)
                left = 2 * idx + 1
                while left < n:
                    smallest = idx
                    if temp_heap[left][0] < temp_heap[smallest][0]:
                        smallest = left
                    right = left + 1
                    if right < n and temp_heap[right][0] < temp_heap[smallest][0]:
                        smallest = right
                    if smallest == idx:
                        break
                    temp_heap[idx], temp_heap[smallest] = temp_heap[smallest], temp_heap[idx]
                    idx = smallest
                    left = 2 * idx + 1
            sorted_elements.append(val)
        
        # Como o min-heap remove do menor para o maior, revertemos o resultado
        # para obter a ordenação decrescente (do maior para o menor)
        return sorted_elements[::-1]


class PageRankCalculator:
    """
    Classe para carregar e calcular o PageRank ponderado sobre grafos de coocorrência.
    Não utiliza nenhuma biblioteca externa de grafos para o cálculo.
    """
    def __init__(self, damping_factor: float = 0.85, max_iter: int = 100, tol: float = 1e-6):
        self.damping_factor = damping_factor
        self.max_iter = max_iter
        self.tol = tol

    def calculate(self, graph: dict, id_to_word: list) -> dict:
        """
        Calcula o PageRank ponderado.
        
        Parâmetros:
        - graph: Dicionário no formato {node_id: {neighbor_id: weight}}
        - id_to_word: Lista mapeando IDs inteiros para palavras (str)
        
        Retorna:
        - Um dicionário mapeando palavras para seus respectivos scores de PageRank.
        """
        N = len(id_to_word)
        if N == 0:
            return {}

        # Normaliza a representação do grafo garantindo chaves numéricas (int)
        normalized_graph = {}
        for u, neighbors in graph.items():
            u_int = int(u)
            normalized_graph[u_int] = {int(v): float(w) for v, w in neighbors.items()}

        # Identifica dangling nodes (nós sem arestas incidentes / força ponderada = 0)
        strength = {}
        dangling_nodes = []
        
        for u in range(N):
            neighbors = normalized_graph.get(u, {})
            s = sum(neighbors.values())
            if s > 0:
                strength[u] = s
            else:
                dangling_nodes.append(u)

        # Inicializa o vetor de PageRank de forma uniforme
        pr = {u: 1.0 / N for u in range(N)}
        d = self.damping_factor

        # Iterações do algoritmo PageRank
        for iteration in range(self.max_iter):
            new_pr = {u: 0.0 for u in range(N)}
            
            # Soma das pontuações dos dangling nodes a serem distribuídas igualmente
            dangling_sum = sum(pr[u] for u in dangling_nodes)
            dangling_contrib = dangling_sum / N
            
            # Contribuição base (fator de teletransporte + dangling nodes)
            base_val = (1.0 - d) / N + d * dangling_contrib
            for u in range(N):
                new_pr[u] = base_val

            # Distribuição de PageRank pelas arestas ponderadas
            for v in range(N):
                if v not in dangling_nodes:
                    neighbors = normalized_graph.get(v, {})
                    for u, w in neighbors.items():
                        new_pr[u] += d * pr[v] * (w / strength[v])

            # Verifica a convergência usando a norma L1 (diferença absoluta total)
            err = sum(abs(new_pr[u] - pr[u]) for u in range(N))
            pr = new_pr
            
            if err < self.tol:
                break

        # Converte as pontuações finais para mapear palavra -> score
        word_pr = {}
        for u in range(N):
            word = id_to_word[u]
            word_pr[word] = pr[u]

        return word_pr

    def get_top_k(self, word_pr: dict, k: int = 15) -> list:
        """
        Extrai as top-K palavras mais centrais usando a estrutura personalizada de Min-Heap.
        
        Retorna:
        - Lista de tuplas (palavra, score) ordenada de forma decrescente por score.
        """
        if not word_pr:
            return []
        
        # Limita K ao número total de elementos
        k = min(k, len(word_pr))
        
        heap = MinHeap(max_size=k)
        for word, score in word_pr.items():
            # Inserimos (score, palavra) no heap
            heap.push((score, word))
            
        # O método get_sorted do Heap retorna em ordem decrescente de score (score, palavra)
        sorted_heap = heap.get_sorted()
        
        # Reformatamos para retornar (palavra, score)
        return [(word, score) for score, word in sorted_heap]
