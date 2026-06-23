import json
import sys
import random
sys.setrecursionlimit(50000)
from src.interface.console import log_dados

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
                "comunidades": self.detectar_comunidade(),
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

    def detectar_comunidade(self, seed=42):
        random.seed(seed)
        componente_para_id=self._componte_como_id()
        comunidade_final={}
        offset=0

        for componente_id in componente_para_id:
            if len(componente_id)==1:
                unico_id=componente_id[0]
                comunidade_final[unico_id]=offset
                offset+=1
                continue

            subgrafo=self._extrair_subgrafo(componente_id)
            particao_local=self._louvain_multinivel(subgrafo)
            ids_locais_unicos = sorted(set(particao_local.values()))
            mapa_local_para_global = {
                local_id: offset + i
                for i, local_id in enumerate(ids_locais_unicos)
            }

            for word_id, local_comm in particao_local.items():
                comunidade_final[word_id] = mapa_local_para_global[local_comm]

            offset += len(ids_locais_unicos)
        return {
            self.id_to_word[word_id]: comm_id
            for word_id, comm_id in comunidade_final.items()
        }


    def _componte_como_id(self):

        visitados = set()
        componentes = []
        for vertice_id in self.graph:
            if vertice_id not in visitados:
                componente = []
                self.dfs(vertice_id, visitados, componente)
                componentes.append(componente)
        return componentes


    def _extrair_subgrafo(self, ids_do_componente):

        ids_set = set(ids_do_componente)
        subgrafo = {}
        for no_id in ids_do_componente:
            subgrafo[no_id] = {
                vizinho: peso
                for vizinho, peso in self.graph[no_id].items()
                if vizinho in ids_set
            }
        return subgrafo

    def _louvain_multinivel(self, grafo_inicial):
        """
        Retorna:
            dict { id_original: community_id }
        """
        EPSILON = 1e-9

        grafo_atual = grafo_inicial

        node_para_no_original = {
            no_id: [no_id] for no_id in grafo_inicial
        }

        Q_anterior = float('-inf')

        while True:
            comunidades_nivel = self._fase1_otimizacao_local(grafo_atual)
            Q_atual = self._calcular_modularidade(grafo_atual, comunidades_nivel)

            if Q_atual - Q_anterior <= EPSILON:
                break

            Q_anterior = Q_atual

            nova_correspondencia = {}
            for no_nivel, comunidade in comunidades_nivel.items():
                for id_original in node_para_no_original[no_nivel]:
                    nova_correspondencia[id_original] = comunidade
            ultima_correspondencia_valida = nova_correspondencia

            n_nos_antes = len(grafo_atual)
            grafo_agregado, node_para_no_original = self._agregar_grafo(
                grafo_atual, comunidades_nivel, node_para_no_original
            )

            if len(grafo_agregado) == n_nos_antes:
                break

            grafo_atual = grafo_agregado

        if Q_anterior == float('-inf'):
            return {no_id: i for i, no_id in enumerate(grafo_inicial)}

        return ultima_correspondencia_valida

    def _fase1_otimizacao_local(self, grafo):
        """
        Retorna:
            dict { no_id: community_id }
        """
        comunidade = {no_id: no_id for no_id in grafo}

        grau = {}
        for no_id in grafo:
            soma = sum(grafo[no_id].values())
            if no_id in grafo[no_id]:
                soma += grafo[no_id][no_id]
            grau[no_id] = soma

        m2 = sum(grau.values())
        if m2 == 0:
            return comunidade

        soma_grau_comunidade = dict(grau)

        nos = list(grafo.keys())
        melhorou_global = True

        while melhorou_global:
            melhorou_global = False
            random.shuffle(nos)

            for no in nos:
                comunidade_atual = comunidade[no]

                soma_grau_comunidade[comunidade_atual] -= grau[no]

                sigma_in_por_comunidade = {}
                for vizinho, peso in grafo[no].items():
                    if vizinho == no:
                        continue  # self-loop não conta como vínculo externo
                    c_vizinho = comunidade[vizinho]
                    sigma_in_por_comunidade[c_vizinho] = (
                            sigma_in_por_comunidade.get(c_vizinho, 0) + peso
                    )

                melhor_comunidade = comunidade_atual
                melhor_ganho = sigma_in_por_comunidade.get(comunidade_atual, 0) - (
                        soma_grau_comunidade[comunidade_atual] * grau[no]
                ) / m2

                for c_candidata, sigma_in in sigma_in_por_comunidade.items():
                    if c_candidata == comunidade_atual:
                        continue
                    ganho = sigma_in - (
                            soma_grau_comunidade.get(c_candidata, 0) * grau[no]
                    ) / m2
                    if ganho > melhor_ganho:
                        melhor_ganho = ganho
                        melhor_comunidade = c_candidata

                soma_grau_comunidade[melhor_comunidade] = (
                        soma_grau_comunidade.get(melhor_comunidade, 0) + grau[no]
                )
                comunidade[no] = melhor_comunidade

                if melhor_comunidade != comunidade_atual:
                    melhorou_global = True

        return comunidade

    def _agregar_grafo(self, grafo, comunidades, node_para_no_original):

        ids_unicos = sorted(set(comunidades.values()))
        remapeamento = {antigo: novo for novo, antigo in enumerate(ids_unicos)}

        novo_grafo = {novo_id: {} for novo_id in remapeamento.values()}

        for no_a in grafo:
            comunidade_a = remapeamento[comunidades[no_a]]
            for no_b, peso in grafo[no_a].items():
                comunidade_b = remapeamento[comunidades[no_b]]

                novo_grafo[comunidade_a][comunidade_b] = (
                        novo_grafo[comunidade_a].get(comunidade_b, 0) + peso
                )

        novo_node_para_no_original = {novo_id: [] for novo_id in remapeamento.values()}
        for no_antigo, comunidade_antiga in comunidades.items():
            novo_id = remapeamento[comunidade_antiga]
            novo_node_para_no_original[novo_id].extend(
                node_para_no_original[no_antigo]
            )

        return novo_grafo, novo_node_para_no_original

    def _calcular_modularidade(self, grafo, comunidades):
        """
        Q = (1 / 2m) * Σ_ij [A_ij - (k_i * k_j) / 2m] * δ(c_i, c_j)

        """
        grau = {}
        for no_id in grafo:
            soma = sum(grafo[no_id].values())
            if no_id in grafo[no_id]:
                soma += grafo[no_id][no_id]
            grau[no_id] = soma

        m2 = sum(grau.values())
        if m2 == 0:
            return 0.0

        soma_interna = 0
        for no_a in grafo:
            for no_b, peso in grafo[no_a].items():
                if comunidades[no_a] == comunidades[no_b]:
                    soma_interna += peso

        soma_grau_por_comunidade = {}
        for no_id in grafo:
            c = comunidades[no_id]
            soma_grau_por_comunidade[c] = soma_grau_por_comunidade.get(c, 0) + grau[no_id]

        soma_graus_quadrado = sum(s * s for s in soma_grau_por_comunidade.values())

        Q = (soma_interna / m2) - (soma_graus_quadrado / (m2 * m2))
        return Q

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
        log_dados(f"{categoria}: {total_vertices} vértices, {total_arestas} arestas")

        builder.save_graph(f"data/graphs/{categoria}_graph.json")

    return builders


