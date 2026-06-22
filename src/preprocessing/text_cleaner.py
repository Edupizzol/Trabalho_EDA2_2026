import spacy


class ReviewPreprocessor:
    def __init__(self):
        self.nlp = spacy.load("pt_core_news_sm")

    def clean_text(self, text: str) -> list:
        if not isinstance(text, str) or not text.strip():
            return []

        doc = self.nlp(text.lower())

        clean_tokens = []
        for token in doc:
            #Filtra stopwords, preposições, pontuações, espaços e números
            if not token.is_stop and not token.is_punct and not token.is_space and not token.like_num:
                #Mantém apenas substantivos e adjetivos
                if token.pos_ in ['NOUN', 'ADJ'] and token.is_alpha:
                    #Adiciona o lema da palavra em português (ex: compro -> comprar)
                    clean_tokens.append(token.lemma_)

        return clean_tokens