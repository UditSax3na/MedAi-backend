from spacy.lang.en.stop_words import STOP_WORDS
import spacy

class NlpClass:
    def __init__(self):
        self.__nlp__ = spacy.load('en_core_web_sm')
        
    def preprocess(self, doc):
        nlp_doc=self.__nlp__(doc)
        d=[]
        for token in nlp_doc:
            if(not token.text.lower()  in STOP_WORDS and  token.text.isalpha()):
                d.append(token.lemma_.lower() )
        return ' '.join(d)

    def preprocess_sym(self, doc):
        nlp_doc=self.__nlp__(doc)
        d=[]
        for token in nlp_doc:
            if(not token.text.lower()  in STOP_WORDS and  token.text.isalpha()):
                d.append(token.lemma_.lower() )
        return ' '.join(d)