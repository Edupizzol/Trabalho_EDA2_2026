import spacy

class ReviewPreprocessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
    def clean_text(self, text: str) -> list:
        
        if not isinstance(text, str) or not text.strip():
            return []
            
        #passa o texto pra minusculo
        doc = self.nlp(text.lower())
        
        clean_tokens = []
        for token in doc:
            #filtra as stopwords preposicoes, pontuações, espaços e números
            if not token.is_stop and not token.is_punct and not token.is_space and not token.like_num:
                #mantém apenas substantivos(NOUN) e adjetivos(ADJ)
                if token.pos_ in ['NOUN', 'ADJ'] and token.is_alpha:
                    #adiciona a raiz da palavra(lemma)
                    clean_tokens.append(token.lemma_)
        return clean_tokens