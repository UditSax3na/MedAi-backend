import pandas as pd
import numpy as np
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from itertools import chain


class SemanticClass:
    def __init__(self, nlp, all_symp_pr, df):
        self.__nlp__=nlp
        self.__all_symp_pr__=all_symp_pr
        self.__df__ = df

    # Word Sense Disambiguation using the Lesk algorithm.
    def __WSD__(self, word, context):
        sens = lesk(context, word)
        return sens

    # Computes the semantic similarity between two documents
    def semanticD(self, doc1, doc2):
        doc1_p = self.__nlp__.preprocess(doc1).split(' ')
        doc2_p = self.__nlp__.preprocess_sym(doc2).split(' ')
        score = 0

        for tock1 in doc1_p:
            for tock2 in doc2_p:
                syn1 = self.__WSD__(tock1, doc1)
                syn2 = self.__WSD__(tock2, doc2)

                if syn1 is not None and syn2 is not None:
                    x = syn1.wup_similarity(syn2)
                    if x is not None and x > 0.1:
                        score += x

        return score / (len(doc1_p) * len(doc2_p))

    # Finds the most semantically similar word in the corpus.
    def semantic_similarity(self, symp_t, corpus):
        max_sim = 0
        most_sim = None

        for symp in corpus:
            d = self.semanticD(symp_t, symp)
            if d > max_sim:
                most_sim = symp
                max_sim = d
        return max_sim, most_sim
    
    def suggest_syn(self, sym):
        symp = []
        synonyms = wn.synsets(sym)  # Get all synsets (meanings) of the word from WordNet
        lemmas = [word.lemma_names() for word in synonyms]  # Extract lemma names (synonyms)
        lemmas = list(set(chain(*lemmas)))  # Flatten list and remove duplicates

        for e in lemmas:
            res, sym1 = self.semantic_similarity(e, self.__all_symp_pr__)  # Compare with all symptoms
            if res != 0:
                symp.append(sym1)

        return list(set(symp))  # Return unique suggested synonyms

    # Receives client symptoms and returns a DataFrame with 1 for associated symptoms.
    def OHE(self, cl_sym, all_sym):
        l = np.zeros([1, len(all_sym)])  # Create a zero array of size (1, number of symptoms)

        for sym in cl_sym:
            l[0, all_sym.index(sym)] = 1  # Mark symptom presence as 1

        return pd.DataFrame(l, columns=all_sym)  # Convert array to DataFrame

    def contains(self, small, big):
        a=True
        for i in small:
            if i not in big:
                a=False
        return a

    def possible_diseases(self, disease, l):
        poss_dis=[]
        for dis in set(disease):
            if self.contains(l,self.symVONdisease(self.__df__,dis)):
                poss_dis.append(dis)
        return poss_dis

    # Receives a disease and returns all associated symptoms
    def symVONdisease(self, df, disease):
        ddf = df[df.prognosis == disease]  # Filter rows where disease matches
        m2 = (ddf == 1).any()  # Find columns (symptoms) with value '1'
        return m2.index[m2].tolist()  # Return symptom names as a list