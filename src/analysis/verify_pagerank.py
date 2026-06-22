import json
import os
import sys

# Garante que a pasta raiz do projeto está no path de importação
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.analysis.pagerank import PageRankCalculator

def verify():
    graph_path = "data/graphs/bad_reviews_graph.json"
    if not os.path.exists(graph_path):
        print(f"Erro: Grafo de teste não encontrado em '{graph_path}'. Certifique-se de que os grafos foram construídos.")
        return

    print("Carregando o grafo...")
    with open(graph_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    graph = data["grafo"]["graph"]
    id_to_word = data["grafo"]["id_to_word"]
    
    # 1. Calcula o PageRank usando a nossa implementação customizada
    print("Calculando o PageRank customizado...")
    calc = PageRankCalculator(damping_factor=0.85, max_iter=100, tol=1e-6)
    custom_pr = calc.calculate(graph, id_to_word)
    
    # 2. Calcula o PageRank usando o NetworkX
    print("Calculando o PageRank com NetworkX para comparação...")
    try:
        import networkx as nx
    except ImportError:
        print("Aviso: NetworkX não está instalado neste ambiente. Não foi possível comparar.")
        return
        
    G = nx.Graph()
    # Adiciona nós explicitamente
    for i in range(len(id_to_word)):
        G.add_node(i)
        
    # Adiciona arestas ponderadas
    for u, neighbors in graph.items():
        u_int = int(u)
        for v, w in neighbors.items():
            v_int = int(v)
            G.add_edge(u_int, v_int, weight=float(w))
            
    # Executa o pagerank ponderado do NetworkX
    # Nota: No NetworkX, o PageRank de grafos não direcionados com pesos trata as arestas como bidirecionais ponderadas
    nx_pr_ids = nx.pagerank(G, alpha=0.85, max_iter=100, tol=1e-6, weight="weight")
    
    # Mapeia os IDs do NetworkX de volta para palavras
    nx_pr = {id_to_word[node_id]: score for node_id, score in nx_pr_ids.items()}
    
    # 3. Compara os resultados
    diffs = []
    print("\n--- Comparação dos Top 10 Termos ---")
    print(f"{'Palavra':<15} | {'Custom PR':<12} | {'NetworkX PR':<12} | {'Diferença':<12}")
    print("-" * 60)
    
    top_custom = calc.get_top_k(custom_pr, 10)
    for word, c_score in top_custom:
        nx_score = nx_pr.get(word, 0.0)
        diff = abs(c_score - nx_score)
        diffs.append(diff)
        print(f"{word:<15} | {c_score:.8f} | {nx_score:.8f} | {diff:.2e}")
        
    for word, nx_score in nx_pr.items():
        c_score = custom_pr.get(word, 0.0)
        diffs.append(abs(c_score - nx_score))
        
    avg_diff = sum(diffs) / len(diffs)
    max_diff = max(diffs)
    print("-" * 60)
    print(f"Diferença Média Absoluta: {avg_diff:.2e}")
    print(f"Diferença Máxima Absoluta: {max_diff:.2e}")
    
    if max_diff < 1e-5:
        print("\n[SUCESSO] A implementação customizada do PageRank está matematicamente CORRETA!")
    else:
        print("\n[ALERTA] Diferença significativa encontrada! Verifique a lógica do algoritmo.")

if __name__ == "__main__":
    verify()
