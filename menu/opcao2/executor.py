import os
import random
from menu.common import pipeline_grafos_e_visualizacao


def executar_opcao_2(cleaned_dir, processed_dir, carregar_func, salvar_func):
    dados = carregar_func(cleaned_dir)
    if not any(dados.values()):
        print("[!] Erro: Dados base não encontrados.")
        return False

    output_opcao_dir = "outputs/menu/opcao2"
    os.makedirs(output_opcao_dir, exist_ok=True)

    dados_selecionados = {"bad_reviews": [], "mid_reviews": [], "good_reviews": []}

    for cat, lista in dados.items():
        print(f"\n==============================================")
        print(f"       CURADORIA MANUAL: {cat.upper()}        ")
        print(f"==============================================")

        # Seleciona uma amostra de 5 para o usuário ler no terminal
        amostra_visualizacao = random.sample(lista, min(len(lista), 5))

        for idx, review in enumerate(amostra_visualizacao, 1):
            print(f"\n[{idx}] {review[:200]}...")
            escolha = input("Deseja incluir essa review no grafo? (s/n): ").lower()
            if escolha == 's':
                dados_selecionados[cat].append(review)

        # Fallback de segurança: caso rejeite todas, escolhe uma aleatória
        if not dados_selecionados[cat] and lista:
            print("[*] Nenhuma review selecionada manualmente. Adicionando uma por amostragem.")
            dados_selecionados[cat].append(random.choice(lista))

    input_amostra_dir = cleaned_dir + "_amostra"
    salvar_func(input_amostra_dir, dados_selecionados)

    # Invoca a função coringa passando os títulos específicos da Opção 2
    pipeline_grafos_e_visualizacao(
        input_amostra_dir=input_amostra_dir,
        processed_dir=processed_dir,
        output_opcao_dir=output_opcao_dir,
        titulo_md="Relatório Executivo - Curadoria e Seleção Manual",
        subtitulo_md="Resultados gerados a partir de reviews validadas e selecionadas a dedo pelo operador."
    )
    return True