import numpy as np
import itertools
import re

class SyntanticClass:
    def __init__(self, all_symp_pr):
        self.__all_symp_pr__ = all_symp_pr

    def jaccard_set(self, str1, str2):
        list1 = str1.split(' ')   # Convert str1 into a list of words
        list2 = str2.split(' ')   # Convert str2 into a list of words
        intersection = len(set(list1).intersection(list2))  # Find common words
        union = (len(list1) + len(list2)) - intersection    # Compute union
        return float(intersection) / union
    
    def syntactic_similarity(self, symp_t, corpus):
        most_sim = []  # Stores similarity scores
        poss_sym = []  # Stores possible matches

        for symp in corpus:
            d = self.jaccard_set(symp_t, symp)  # Compute Jaccard similarity
            most_sim.append(d)

        order = np.argsort(most_sim)[::-1].tolist()  # Sort by similarity (descending)

        for i in order:
            if self.DoesExist(symp_t):  # If an exact match exists
                return 1, [corpus[i]]
            if corpus[i] not in poss_sym and most_sim[i] != 0:
                poss_sym.append(corpus[i])

        if len(poss_sym):
            return 1, poss_sym  # Return possible matches
        else:
            return 0, None  # No match found

    # Returns all the subsets of this set. This is a generator.
    def powerset(self, seq):
        if len(seq) <= 1:
            yield seq  # Return single element
            yield []   # Return empty subset
        else:
            for item in self.powerset(seq[1:]):  # Recursive call for remaining elements
                yield [seq[0]] + item
                yield item

    # Sort list based on length
    def sort(self, a):
        for i in range(len(a)):
            for j in range(i+1, len(a)):
                if len(a[j]) > len(a[i]):  # Compare lengths
                    a[i], a[j] = a[j], a[i]  # Swap if necessary
        a.pop()  # Remove smallest subset
        return a

    # find all permutations of a list
    def permutations(self, s):
        permutations = list(itertools.permutations(s))
        return [' '.join(permutation) for permutation in permutations]

    def DoesExist(self, txt):
        txt=txt.split(' ')
        combinations = [x for x in self.powerset(txt)]
        self.sort(combinations)
        for comb in combinations :
            for sym in self.permutations(comb):
                if sym in self.__all_symp_pr__:
                    return sym
        return False

    def check_pattern(self, inp, dis_list):
        pred_list=[]
        ptr=0
        patt = "^" + inp + "$"
        regexp = re.compile(inp)
        for item in dis_list:
            if regexp.search(item):
                pred_list.append(item)
        if(len(pred_list)>0):
            return 1,pred_list
        else:
            return ptr,None