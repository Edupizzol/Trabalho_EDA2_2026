# Relatório de Vizinhança Semântica via Busca em Largura (BFS)

Este relatório utiliza o algoritmo de busca em largura a partir das palavras-âncora do PageRank 
para rastrear o contexto de avaliação dos usuários em 1 e 2 saltos de distância.

## 📊 Categoria: BAD_REVIEWS

### 🔍 Palavra-Raiz: `produto`
* **Conexões Diretas (Distância 1):** empresa (12), problema (9), semana (9), dinheiro (8), compra (7), entrega (6), americana (6), defeito (6)
* **Contexto Estendido (Distância 2):** erro, feliz, abusivo, culpa, frete, pessoal, site, controle, casa, celular

### 🔍 Palavra-Raiz: `dia`
* **Conexões Diretas (Distância 1):** entrega (7), americana (7), produto (6), útil (6), fogão (4), defeito (4), informação (4), uso (4)
* **Contexto Estendido (Distância 2):** março, transtorno, pequeno, rótulo, atraso, pesado, ligação, financeiro, pessoa, correio

### 🔍 Palavra-Raiz: `americana`
* **Conexões Diretas (Distância 1):** dia (7), site (7), produto (6), compra (6), contato (5), compro (5), cliente (4), problema (4)
* **Contexto Estendido (Distância 2):** entrega, útil, fogão, defeito, informação, uso, impressora, envio, cama, novembro

### 🔍 Palavra-Raiz: `compra`
* **Conexões Diretas (Distância 1):** produto (7), dinheiro (6), americana (6), problema (4), defeito (3), parceiro (3), data (3), bom (2)
* **Contexto Estendido (Distância 2):** empresa, semana, entrega, volta, ruim, foto, correto, técnico, resposta, incoerente

### 🔍 Palavra-Raiz: `uso`
* **Conexões Diretas (Distância 1):** dia (4), celular (4), problema (3), bonito (2), pilha (2), produto (2), eficácia (2), modo (2)
* **Contexto Estendido (Distância 2):** entrega, americana, útil, fogão, impressora, envio, cama, novembro, impressão, prazo

## 📊 Categoria: MID_REVIEWS

### 🔍 Palavra-Raiz: `produto`
* **Conexões Diretas (Distância 1):** acabamento (8), razoável (7), qualidade (5), compra (4), entrega (4), rápido (4), potente (3), expectativa (3)
* **Contexto Estendido (Distância 2):** designer, desempenho, funcionamento, aparelho, controle, assento, pequenininha, indico, fixação, antigo

### 🔍 Palavra-Raiz: `entrega`
* **Conexões Diretas (Distância 1):** prazo (5), rápido (4), produto (4), americana (2), fevereiro (2), ótimo (2), serviço (2), caso (2)
* **Contexto Estendido (Distância 2):** excelente, correio, direitinho, retirada, residência, combinado, parceiro, baixo, indico, funcionando

### 🔍 Palavra-Raiz: `prazo`
* **Conexões Diretas (Distância 1):** entrega (5), americana (3), excelente (3), correio (2), direitinho (2), gente (2), dia (2), alto (2)
* **Contexto Estendido (Distância 2):** serviço, caso, loja, super, expectativa, embalar, atraso, perfeito, horrível, greve

### 🔍 Palavra-Raiz: `preço`
* **Conexões Diretas (Distância 1):** acessível (4), acessório (2), jogo (2), má (2), caro (2), produto (2), fácil (2), justo (2)
* **Contexto Estendido (Distância 2):** bom, armazenamento, anterior, requisito, fifa, valor, expectativa, acabamento, razoável, qualidade

### 🔍 Palavra-Raiz: `aparelho`
* **Conexões Diretas (Distância 1):** ano (2), respeito (2), desempenho (2), fomato (2), peça (2), ruim (2), critica (2), opção (2)
* **Contexto Estendido (Distância 2):** amigo, passado, factor, banco, troféu, jeito, perfeito, yamaha, volta, necessidade

## 📊 Categoria: GOOD_REVIEWS

### 🔍 Palavra-Raiz: `produto`
* **Conexões Diretas (Distância 1):** qualidade (13), excelente (11), prazo (8), ótimo (5), preço (3), macio (3), caixa (3), entrega (3)
* **Contexto Estendido (Distância 2):** necessidade, rápido, embalado, péssimo, foto, indiscutível, pratico, necessário, felicidade, probema

### 🔍 Palavra-Raiz: `qualidade`
* **Conexões Diretas (Distância 1):** produto (13), ótimo (10), entrega (6), excelente (5), prazo (3), necessidade (3), rápido (2), bonito (2)
* **Contexto Estendido (Distância 2):** caixa, ammericcanna, frágil, perfeito, bom, velcro, barato, presta, maravilhoso, loja

### 🔍 Palavra-Raiz: `excelente`
* **Conexões Diretas (Distância 1):** produto (11), bom (5), qualidade (5), imagem (4), android (2), câmera (2), satisfeito (2), data (2)
* **Contexto Estendido (Distância 2):** caixa, ammericcanna, material, frágil, velcro, barato, presta, maravilhoso, loja, pena

### 🔍 Palavra-Raiz: `prazo`
* **Conexões Diretas (Distância 1):** entrega (9), produto (8), dia (4), qualidade (3), perfeito (2), longo (2), recomendo (2), super (2)
* **Contexto Estendido (Distância 2):** embalado, logístico, expectativa, caixa, livro, educação, utel, recomendar, ótimo, papelão

### 🔍 Palavra-Raiz: `entrega`
* **Conexões Diretas (Distância 1):** prazo (9), rápido (9), qualidade (6), dia (3), produto (3), embalado (2), excelente (2), recomendo (2)
* **Contexto Estendido (Distância 2):** problema, rede, cakes, pedido, acabamento, encosto, atônico, mouse, moto, bonito
