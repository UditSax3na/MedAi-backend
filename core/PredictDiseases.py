import pandas as pd
import numpy as np
import joblib
import os
import csv
import pickle

from nltk.corpus import wordnet as wn
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

from ..Constants.path import *
from .NlpClass import *

class PredictDiseases:
    def __init__(self):
        self.__df__ = pd.read_csv(TRUE_DATASET)
        self.__all_symp_col__ = list(self.__df__.columns[:-1])
        self.__all_symp__ = [self.__clean_symp__(sym) for sym in self.__all_symp_col__]
        self.__nlp__ = NlpClass()
        self.__all_symp_pr__=[self.__nlp__.preprocess_sym(sym) for sym in self.__all_symp__]
        self.__col_dict__ = {}
        if CLEANSYM_DATASET.exists():
            self.loadZipDic()
        else:
            self.__col_dict__ = dict(zip(self.__all_symp_pr__, self.__all_symp_col__))
            self.saveZipDic()
        self.__X__ = self.__df__.iloc[:, :-1]
        self.__le__ = joblib.load(LENCODER_PATH) if not(os.path.exists(LENCODER_PATH)) else LabelEncoder()
        self.__y__ = self.__le__.fit_transform(self.__df__.iloc[:, -1])
        self.X_train, self.Y_train, self.X_test, self.Y_test = self.__train_test_split__()
        self.__model__ = joblib.load(KNNMODEL_PATH) if os.path.exists(KNNMODEL_PATH) else self.__create_model__()
        self.__severityDictionary__ = {}
        self.__description_list__ = {}
        self.__precautionDictionary__ = {}
        self.__symp__=[]
        self.__disease__=[]
        for i in range(len(self.__df__)):
            self.__symp__.append(self.__df__.columns[:-1].to_list())
            self.__disease__.append(self.__df__.iloc[i,-1])

    def __create_model__(self):
        model = KNeighborsClassifier(n_neighbors=5)
        model.fit(self.X_train, self.Y_train)
        y_pred = model.predict(self.X_test)  
        print(f"Accuracy: {accuracy_score(self.Y_test, y_pred)}")
        print(f"Classification Report : {classification_report(self.Y_test, y_pred)}")
        self.__saveModel__()

    def __train_test_split__(self):
        return train_test_split(self.__X__, self.__y__, test_size=0.2, random_state=42)

    def __saveModel__(self):
        joblib.dump(self.__model__, KNNMODEL_PATH)

    def __saveEncoder__(self):
        joblib.dump(self.__le__, SAVED_ENCODER_PATH)

    def __clean_symp__(self, sym:str):
        return sym.replace('_',' ').replace('.1','').replace('(typhos)','').replace('yellowish','yellow').replace('yellowing','yellow')

    def encode_symptoms(self, user_symptoms, all_symptoms):
        user_symptoms = [sym.replace(" ", "_") for sym in user_symptoms]
        encoded_vector = np.zeros(len(all_symptoms))
        for symptom in user_symptoms:
            if symptom in all_symptoms:
                encoded_vector[all_symptoms.index(symptom)] = 1

        return [encoded_vector]  # Ensure it's in 2D format for prediction

    def predict_disease(self, user_symptoms, all_symptoms, label_encoder):
        """
        used to predict the disease from the user given symptoms
        """
        user_symptoms = [sym.replace(" ", "_") for sym in user_symptoms]
        encoded_input = self.encode_symptoms(user_symptoms, all_symptoms)
        encoded_input_df = pd.DataFrame(encoded_input, columns=all_symptoms)
        predicted_label = self.__model__.predict(encoded_input_df)[0]
        return label_encoder.inverse_transform([predicted_label])[0]

    def getDescription(self):
        """
        used to read the description from the description datasets
        """
        with open(DESCRIPTION_DATASET) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                _description={row[0]:row[1]}
                self.__description_list__.update(_description)

    def getSeverityDict(self):
        """
        used to read the severity from the serverity datasets
        """
        with open(SEVERITY_DATASET) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            try:
                for row in csv_reader:
                    _diction={row[0]:int(row[1])}
                    self.__severityDictionary__.update(_diction)
            except:
                pass

    def getprecautionDict(self):
        """
        used to read the precaution from the precaution datasets
        """
        with open(PRECAUTION_DATASET) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                _prec={row[0]:[row[1],row[2],row[3],row[4]]}
                self.__precautionDictionary__.update(_prec)

    def saveZipDic(self):
        """
        use to save the __col_dict__ which contain the cleaned symptoms and symptoms from the og dataset
        """
        with open(CLEANSYM_DATASET, "wb") as f:
            pickle.dump(self.__col_dict__, f)

    def loadZipDic(self):
        """
        used to load the file and get the cleaned and non cleaned values
        """
        with open(CLEANSYM_DATASET, "rb") as f:
            self.__col_dict__ = pickle.load(f)