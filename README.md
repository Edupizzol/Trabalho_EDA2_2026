# Trabalho_EDA2_2026

## Análise de Utilidade em Reviews de E-commerce por meio de Grafos de Coocorrência

### Descrição

Este projeto tem como objetivo investigar quais características tornam uma avaliação de produto útil para outros consumidores em plataformas de e-commerce.

A análise será realizada utilizando o dataset **B2W Reviews**, composto por avaliações de clientes das plataformas Americanas, Submarino e Shoptime. Como medida de engajamento, será utilizada a quantidade de votos recebidos na pergunta *"Esta avaliação foi útil?"*.

A partir dos textos das avaliações serão construídos **grafos de coocorrência de palavras**, permitindo identificar padrões estruturais do discurso presente em reviews com diferentes níveis de utilidade.

---

## Objetivos

* Realizar o pré-processamento textual das avaliações.
* Construir grafos de coocorrência de palavras.
* Comparar avaliações com alta e baixa utilidade.
* Identificar palavras centrais e comunidades temáticas.
* Investigar se reviews considerados úteis apresentam maior presença de termos técnicos, descritivos ou emocionais.

---

## Hipótese

Avaliações consideradas úteis tendem a apresentar descrições mais detalhadas sobre características do produto, formando redes semânticas mais densas e especializadas.

Por outro lado, avaliações pouco úteis tendem a concentrar-se em opiniões genéricas e expressões emocionais, gerando estruturas menos informativas.

---

## Dataset

O projeto utiliza o dataset **B2W Reviews** disponível no Kaggle.

Após o download, o arquivo deve ser colocado em:

```text
data/raw/
```

Exemplo:

```text
data/raw/B2W-Reviews01.csv
```

---

## Instalação e Execução

### Pré-requisitos

- Python 3.13 ou superior
- Poetry (gerenciador de dependências)

### Instalando Poetry

Se você ainda não tem o Poetry instalado, siga as instruções em: https://python-poetry.org/docs/#installation

No Windows, você pode instalar com:
```bash
pipx install poetry
```

Ou usando pip:
```bash
pip install poetry
```

### Instalando as Dependências

Clone o repositório e navegue até o diretório do projeto:

```bash
cd Trabalho_EDA2_2026
```

Instale as dependências usando Poetry:

```bash
poetry install
```

Isso criará um ambiente virtual e instalará todos os pacotes listados em `pyproject.toml`.

### Ativando o Ambiente Virtual

Para ativar o ambiente virtual criado pelo Poetry:

```bash
poetry shell
```

Ou você pode executar comandos diretamente sem ativar com:

```bash
poetry run python main.py
```

### Executando o Projeto

Após instalar as dependências e ativar o ambiente virtual, você pode executar o projeto:

```bash
python main.py
```

Ou sem ativar o ambiente:

```bash
poetry run python main.py
```

---

## Estrutura do Projeto

```text
Trabalho_EDA2_2026/
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   ├── processed/
│   └── graphs/
│
├── src/
│   ├── extraction/
│   ├── preprocessing/
│   ├── graph_definition/
│   ├── graph_construction/
│   ├── analysis/
│   └── utils/
│
├── outputs/
│   ├── figures/
│   ├── metrics/
│   └── reports/
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Pipeline

### 1. Extração

Leitura e seleção dos dados relevantes do dataset.

### 2. Pré-processamento

* Conversão para minúsculas
* Remoção de pontuação
* Remoção de stopwords
* Tokenização

### 3. Construção do Grafo

Cada palavra corresponde a um nó.

Uma aresta é criada quando duas palavras aparecem na mesma avaliação.

O peso da aresta corresponde ao número de avaliações em que a coocorrência foi observada.

### 4. Análise de Redes

Serão avaliadas métricas como:

* Grau
* Betweenness Centrality
* Eigenvector Centrality
* PageRank
* Comunidades (Louvain)

### 5. Comparação de Utilidade

Serão construídos grafos independentes para:

* Reviews com alta utilidade
* Reviews com baixa utilidade

Os resultados serão comparados para identificar diferenças estruturais no discurso.

---

## Tecnologias

* Python
* Pandas
* NetworkX
* NumPy
* Matplotlib
* Seaborn
* NLTK / SpaCy

---

## Resultados Esperados

* Identificação das palavras mais influentes em reviews úteis.
* Descoberta de comunidades temáticas relacionadas a aspectos do produto.
* Comparação estrutural entre avaliações úteis e não úteis.
* Visualizações de redes de coocorrência.

---

## Autores

Projeto desenvolvido para a disciplina de Estruturas de Dados e Algoritmos II (EDA II).
