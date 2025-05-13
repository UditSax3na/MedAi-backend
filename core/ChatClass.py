from .PredictDiseases import PredictDiseases
from .SemanticClass import SemanticClass
from .SyntanticClass import SyntanticClass

class ChatClass:
    def __init__(self):
        self.__pd__ = PredictDiseases()
        self.__sem__ = SemanticClass(self.__pd__.__nlp__, self.__pd__.__all_symp_pr__, self.__pd__.__df__)
        self.__syn__ = SyntanticClass(self.__pd__.__all_symp_pr__)
        self.sim1 = None
        self.sim2 = None
        self.sym1 = None
        self.psym1 = None
        self.psym2 = None
        self.user_inputs = []
        self.diseases =  self.__pd__.__disease__
        self.all_sym = []
        self.result = None

    @classmethod
    def dict_from(cls, data):
        obj = cls()
        obj.sim1 = data["sim1"]
        obj.sim2 = data["sim2"]
        obj.sym1 = data["sym1"]
        obj.psym1 = data["psym1"]
        obj.psym2 = data["psym2"]
        obj.user_inputs = data["user_inputs"]
        obj.result = data["result"]
        return obj

    def to_dict(self):
        return {
            "sim1": self.sim1,
            "sim2": self.sim2,
            "sym1": self.sym1,
            "psym1": self.psym1,
            "psym2": self.psym2,
            "result": self.result,
            "user_inputs": self.user_inputs
        }

    def calc_condition(self, exp, days):
        sum = 0
        for item in exp:
            if item in self.__pd__.__severityDictionary__.keys():
                sum += self.__pd__.__severityDictionary__[item]
        if ((sum * days) / (len(exp))) > 13:
            return "You should take the consultation from doctor."
        else:
            return "It might not be that bad but you should take precautions."

    def related_sym(self,sym, psym1, key: int):
        m = [self.__pd__.__clean_symp__(it) for num, it in enumerate(psym1)]
        if len(m)==1:
            if m[0].lower() == sym.lower():
                return sym
        else:
            dic = {
                "q": "searches related to input: ",
                "qkey": key + 1,
                "ic": -1,
                "ql": [],
                "p": None,
                "r": None
            }
            dic["ql"] = m
            return dic

    def main_sp(self, name, all_symp_col, answer: dict):
        print(f"This is answer : {answer}")
        dic = {
            "q": "Enter the main symptom you are experiencing Mr/Ms " + name,
            "qkey": 1,
            "ic": -1,
            "ql": [],
            "p": None,
            "r": None
        }

        if answer['qkey'] == 0 :
            if answer['answer'].lower() == 'yes':
                return dic, 0
            return dic, 0
        
        elif answer['qkey'] in [1, 2]:
            a, self.sim1, self.psym1 = self.first_initial_sym(self.sym1, self.sim1, answer)
            self.sym1 = self.psym1
            if isinstance(a, dict) and self.sim1 == None:
                print("we are here 1!")
                print(f"a:{a}, self.sim1:{self.sim1}, self.psym1:{self.psym1}")
                return a, 0
            else:
                print("we are here 1!")
                self.user_inputs.append(self.psym1)
                dic["q"] = "Enter a second symptom you are experiencing Mr/Ms " + name
                dic["qkey"] = 3
                print(f"a:{a}, self.sim1:{self.sim1}, self.psym1:{self.psym1}")
                return dic, 0
            
        elif answer['qkey'] in [3, 4]:
            a, self.sim2, self.psym2 = self.first_initial_sym(self.sym1, self.sim2, answer)
            self.sym1 = self.psym2
            if isinstance(a, dict) and self.sim2 == None:
                print("we are here 1!")
                return a, 0
            else:
                print("we are here 2!")
                self.user_inputs.append(self.psym2)
                if self.sim1 == 0 or self.sim2 == 0:
                    self.sim1, self.psym1 = self.__sem__.semantic_similarity(self.user_inputs[0], self.__pd__.__all_symp_pr__)
                    self.sim2, self.psym2 = self.__sem__.semantic_similarity(self.user_inputs[1], self.__pd__.__all_symp_pr__)
                if self.sim1 == 0 and self.sim2 == 0:
                    dic.update({
                        "q":"Could not understand symptoms. Please re-enter.", 
                        "qkey": 0,
                        "ic":-1,
                        "ql": [],
                        "p": None,
                        "r": None
                    })
                    return dic, None
                if self.sim1 == 0:
                    self.psym1 = self.psym2
                if self.sim2 == 0:
                    self.psym2 = self.psym1
                self.all_sym = [self.__pd__.__col_dict__[self.psym1], self.__pd__.__col_dict__[self.psym2]]
                self.diseases = self.__sem__.possible_diseases(disease = self.diseases, l = self.all_sym)
                if len(self.diseases)==0:
                    return dic.update({
                        "q":"I can't find anything with these symptoms can you change symptoms (yes):", 
                        "qkey": 0,
                        "ic":-1,
                        "ql": [],
                        "p": None,
                        "r": None
                    })
                print(f"self.diseases : {self.diseases}")
                dic['ic']=answer['ic']+1
                ql = []
                k = self.__sem__.symVONdisease(self.__pd__.__df__, self.diseases[dic['ic']])
                ql.extend(k)
                print(f"this is the ql: {ql}")
                ql = list(set(ql))
                self.__pd__.getSymDesc()
                ql = [[i, self.__pd__.__symDesc__[i]] for i in ql if i.replace("_"," ") not in self.user_inputs] 
                print(f"this is the ql: {ql} and this is user_inputs: {self.user_inputs}")
                dic["q"] = "Are you experiencing any of the following?"
                dic["ql"] = ql
                dic["qkey"] = 5
                return dic, 0
                
        elif answer['qkey'] == 5:
            print("flag: 0")
            if isinstance(answer['answer'], list):
                self.user_inputs.extend(answer['answer'])
                self.all_sym.extend(answer['answer'])

                self.user_inputs = list(set(self.user_inputs))
                self.all_sym = list(set(self.all_sym))

            self.diseases = self.__sem__.possible_diseases(disease = self.diseases, l = self.all_sym)
            print(f"self.diseases : {self.diseases}")
            if len(self.diseases)==1:
                print("flag: 1")
                pred = self.__pd__.__model__.predict(self.__sem__.OHE(self.all_sym, all_symp_col))
                print(f"pred, self.all_sym: {pred}, {self.all_sym}")
                return pred, 1
            else:
                print("flag: 2")
                print(f"self.diseases : {self.diseases}")
                ql = []
                for dis in self.diseases:
                    k = self.__sem__.symVONdisease(self.__pd__.__df__, dis)
                    ql.extend(k)
                
                newql = []
                for i in ql:
                    if i not in answer['answer']:
                        newql.append(i)

                print(f"this is the ql: {ql}")
                ql = list(set(ql))
                print(f"this is the ql: {ql}")
                dic['ic']=answer['ic']+1
                dic["q"] = "Are you experiencing any of the following?"
                dic["ql"] = newql
                dic["qkey"] = 5
                return dic, 0

    def chat_sp(self, name, answer: dict):
        dic = {
            "q": "Enter the main symptom you are experiencing Mr/Ms " + name,
            "qkey": 1,
            "ic": -1,
            "ql": [],
            "p": None,
            "r": None
        }
        if answer['qkey'] < 10:
            result, sym = self.main_sp(name, self.__pd__.__all_symp_col__, answer)
            print(f"this is result, sym : {result}, {sym}")
            
        else:
            sym = 1

        if sym == 1:
            if answer["qkey"] < 10:
                self.__pd__.getDescription()
                self.__pd__.getSeverityDict()
                self.__pd__.getprecautionDict()
                result = self.__pd__.__le__.inverse_transform([result[0]])[0]
                self.result = result
                if result is None:
                    dic['q'] = "Can you specify more what you feel or tap q to stop the conversation"
                    dic['qkey'] = 11
                    return dic
                
                else:
                    dic['p'] = result
                    self.result = result
                    dic['q'] = "How many days do you feel those symptoms?"
                    dic['r']={
                        "desc":self.__pd__.__description_list__[self.result],
                        "prec":self.__pd__.__precautionDictionary__[self.result]
                    }
                    dic['qkey'] = 11
                    return dic
                
            elif answer['qkey'] == 11:
                res = self.calc_condition(self.all_sym, int(answer['answer']))
                dic['r'] = res
                dic['q'] = "Do you need another medical consultation? (yes or no)"
                dic['qkey'] = 12
                return dic
            
            elif answer['qkey'] == 12:
                if answer['answer'].lower() != "yes":
                    # dic['qkey'] = 0
                    dic['r'] = "Thank you for using our application!"
                    dic['qkey']=200
                    return dic
                
                else:
                    return {
                        "q": "Enter the main symptom you are experiencing Mr/Ms " + name,
                        "qkey": 0,
                        "ic": -1,
                        "ql": [],
                        "p": None,
                        "r": None
                    }
                
            else:
                dic['q'] = "Error: Invalid qkey"
                dic['qkey'] = -2
                return dic
        else:
            return result

    def first_initial_sym(self, dfsym, sim, answer):
        if answer["qkey"] in [1, 3]:
            sym = self.__pd__.__nlp__.preprocess_sym(answer['answer'])
            sim, psym = self.__syn__.syntactic_similarity(sym, self.__pd__.__all_symp_pr__)
            if sim == 1:
                a = self.related_sym(sym, psym, answer["qkey"])
                if isinstance(a, str) and a == sym:
                    return sym, sim, a
                return a, None, None
            return sym, sim, answer['answer']
        return dfsym, sim, answer['answer']