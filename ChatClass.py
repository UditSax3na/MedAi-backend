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

    def calc_condition(self, exp, days):
        sum = 0
        for item in exp:
            if item in self.__pd__.__severityDictionary__.keys():
                sum += self.__pd__.__severityDictionary__[item]
        if ((sum * days) / (len(exp))) > 13:
            return "You should take the consultation from doctor.", 1
        else:
            return "It might not be that bad but you should take precautions.", 0

    def related_sym(self,sym, psym1, key: int):
        m = [f"{num}) {self.__pd__.__clean_symp__(it)}" for num, it in enumerate(psym1)]
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
            print(f"psym1 : {psym1} and enumerate(psym1) : {enumerate(psym1)}")
            dic["ql"] = m
            print(f'this is dic : {dic}')
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

        if answer['qkey'] == 0:
            return dic, 0
        elif answer['qkey'] in [1, 2]:
            a, self.sim1, self.psym1 = self.first_initial_sym(self.sym1, self.sim1, answer)
            if isinstance(a, dict) and self.sim1 == None and self.psym1==None:
                return a, 0
            else:
                self.sym1 = a
                self.user_inputs.append(a)
                dic["q"] = "Enter a second symptom you are experiencing Mr/Ms " + name
                dic["qkey"] = 3
                return dic, 0
        elif answer['qkey'] == 3:
            a, self.sim2, self.psym2 = self.first_initial_sym(self.sym1, self.sim2, answer)
            if isinstance(a, dict) and self.sim2 == None and self.psym1==None:
                return a, 0
            else:
                self.sym2 = a
                self.user_inputs.append(a)
                if self.sim1 == 0 or self.sim2 == 0:
                    self.sim1, self.psym1 = self.__sem__.semantic_similarity(self.user_inputs[0], self.__pd__.__all_symp_pr__)
                    self.sim2, self.psym2 = self.__sem__.semantic_similarity(self.user_inputs[1], self.__pd__.__all_symp_pr__)

                if self.sim1 == 0 and self.sim2 == 0:
                    return {"q": "Could not understand symptoms. Please re-enter.", "qkey": 0}, None
                if self.sim1 == 0:
                    self.psym1 = self.psym2
                if self.sim2 == 0:
                    self.psym2 = self.psym1
                self.psym2 = int(self.psym2) if self.psym2.isdigit() else self.psym2
                self.psym1 = int(self.psym1) if self.psym1.isdigit() else self.psym1
                self.all_sym = [self.__pd__.__col_dict__[self.psym1], self.__pd__.__col_dict__[self.psym2]]
                print(f"This is self.diseases : {self.diseases}")
                self.diseases = self.__sem__.possible_diseases(disease=self.diseases, l=self.all_sym)
                dic["ic"] += 1
                k = self.__sem__.symVONdisease(self.__pd__.__df__, self.diseases[dic["ic"]])
                dic["ql"] = k
                dic["qkey"] = 4
                dic["q"] = "Are you experiencing any of the following?"
                return dic, 0
        elif answer['qkey'] == 4:
            if isinstance(answer['answer'], str):
                self.user_inputs.append(answer['answer'])
                self.all_sym.append(answer['answer'])

            self.diseases = self.__sem__.possible_diseases(disease = self.diseases, l=self.all_sym)
            if len(self.diseases) == 1:
                pred = self.__pd__.__model__.predict(self.__sem__.OHE(self.all_sym, all_symp_col))
                return pred, self.all_sym
            else:
                dic["ic"] += 1
                print(f"self.diseases : {self.diseases}")
                k = self.__sem__.symVONdisease(self.__pd__.__df__, self.diseases[dic["ic"]])
                dic["q"] = "Are you experiencing any of the following?"
                dic["ql"] = k
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
        else:
            sym = 1

        if sym == 1:
            if answer["qkey"] < 10:
                result = self.__pd__.__le__.inverse_transform([result[0]])[0]
                if result is None:
                    dic['q'] = "Can you specify more what you feel or tap q to stop the conversation"
                    dic['qkey'] = 11
                    return dic
                else:
                    dic['p'] = "You may have " + result
                    self.r = result
                    dic['q'] = "How many days do you feel those symptoms?"
                    dic['qkey'] = 12
                    return dic
            elif answer['qkey'] == 11:
                if answer['answer'] == "q":
                    self.user_inputs = []
                    dic['q'] = None
                    dic['qkey'] = -1
                    return dic
                else:
                    answer['qkey'] = 0
                    return self.chat_sp(name, answer)
            elif answer['qkey'] == 12:
                _, flag = self.calc_condition(self.all_sym, int(answer['answer']))
                dic['response'] = (
                    "You should take the consultation from doctor" if flag == 1 
                    else self.__pd__.__precautionDictionary__[self.result]
                )
                dic['q'] = "Do you need another medical consultation? (yes or no)"
                dic['qkey'] = 13
                return dic
            elif answer['qkey'] == 13:
                if answer['answer'].lower() != "yes":
                    dic['qkey'] = -1
                    dic['response'] = "Thank you for using our application!"
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
                return {"q": "Error: Invalid qkey"}
        else:
            return result

    def first_initial_sym(self, sym, sim, answer):
        if answer["qkey"] in [1, 3]:
            sym = self.__pd__.__nlp__.preprocess_sym(answer['answer'])
            sim, psym = self.__syn__.syntactic_similarity(sym, self.__pd__.__all_symp_pr__)
            print(f"sym, psym, sim :{sym}, {psym}, {sim}")
            if sim == 1:
                a = self.related_sym(sym, psym, answer["qkey"])
                if a == sym:
                    return sym, sim, answer['answer'] 
                return a, None, None
            else:
                return sym, sim, answer['answer']
        else:
            return sym, sim, answer['answer']
