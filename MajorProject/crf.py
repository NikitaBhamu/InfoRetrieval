import numpy as np
import os
import json
from nltk.stem import PorterStemmer
import collections
from scipy import spatial
import re
import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from rake_nltk import Rake
import numpy as np
from evaluate import *
from bm25 import *
rake_nltk_var = Rake()

porter = PorterStemmer()

def getTerms(text):
    terms = []
    text = text.lower()
    words = re.split(r'[\n`;\-,\s.>?:"\'\[\](){}@#+!_~&*%^=|$/<>]\s*', text)
    #words = word_tokenize(review)
    for word in words:
        if word!='':
            terms.append(word)
    return terms

def getQueriesData(filename='../data/CANARD_Release/train.json'):
    queries = {}
    traindata = json.load(open(filename))
    X_test = []
    for i, conversation in enumerate(traindata):
        if(i+1 < len(traindata) and traindata[i+1]['Question_no']==1):
            qid = conversation["QuAC_dialog_id"]+'@'+str(conversation["Question_no"])
            history = " ".join(conversation["History"])
            rake_nltk_var.extract_keywords_from_text(history)
            keyword_extracted = rake_nltk_var.get_ranked_phrases()[0]
            text = keyword_extracted[0] + ' ' + conversation["Question"]
            queries[qid] = text
            featureDict = [{'word': term} for term in text.split(' ')]
            X_test.append(featureDict)
        if(len(X_test)==100): break
    return queries, X_test

def getIdealQueriesData(filename='../data/CANARD_Release/train.json'):
    queries = {}
    traindata = json.load(open(filename))
    X_train = []
    for i, conversation in enumerate(traindata):
        if(i+1 < len(traindata) and traindata[i+1]['Question_no']==1):
            qid = conversation["QuAC_dialog_id"]+'@'+str(conversation["Question_no"])
            text = conversation["Rewrite"]
            queries[qid] = text
            rake_nltk_var.extract_keywords_from_text(text)
            keywords = rake_nltk_var.get_ranked_phrases()
            featureDict = [{'word': term} for term in keywords]

            #featureDict = [{'word': term} for term in text.split(' ')]
            X_train.append(featureDict)
        if(len(X_train)==100): break
    return queries, X_train

queries, X_train = getIdealQueriesData()
queries, X_test = getQueriesData()
ranked_queries = list(rankBM25(corpus, queries, 1).values())
print(len(X_train),len(X_test))
print((X_train)[0],(X_test)[0])
y_train=[]
for i,example in enumerate(X_train):
    y_train.append([ranked_queries[i][0] for ex in example])
y_test = []
for i,example in enumerate(X_test):
    y_test.append([ranked_queries[i][0] for ex in example])

print("TRAINING START")

crf = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=100,
    all_possible_transitions=True
)

crf.fit(X_train, y_train)
labels = list(crf.classes_)

y_pred = crf.predict(X_train)

print("Train accuracy:", metrics.flat_f1_score(y_train, y_pred,
average='weighted', labels=labels))

y_pred = crf.predict(X_test)
print("Test accuracy:", metrics.flat_f1_score(y_test, y_pred,
average='weighted', labels=labels))
