import numpy as np
import pandas as pd
import os
import json
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
from nltk.corpus import stopwords
from bs4 import BeautifulSoup as bs
import time
import collections
from scipy import spatial
import re
import sys
import math

def evaluate(ranked_queries, topDocs_queries, queries, N):
    mrr = 0
    meanap = 0
    fscores = 0
    recall = 0
    precision = 0
    for query in queries:
        avgp = 0
        # results = []
        mrrq = -1
        topDocs = topDocs_queries[query]
        ranked = ranked_queries[query]
        tp = len(set(topDocs).intersection(set(ranked)))
        fn = len(topDocs) - tp
        fp = len(ranked) - tp
        fscores += tp/(tp+(fp+fn)/2)
        recall += tp/(tp+fn)
        precision += tp/(tp+fp)
        for i in range(len(ranked)):
            if(ranked[i] in topDocs and mrrq == -1): mrrq = 1/(i+1)
            # if(ranked[i] in topDocs): results.append(1)
            # else: results.append(0)
            # prej = np.sum(np.array(results))/len(results)
            # avgp += prej
        meanap += avgp/100
        if mrrq!=-1:
            mrr += mrrq
    print('MRR: ', mrr/len(queries), 'Avg F1 score: ', fscores/len(queries),'Avg Precision: ', precision/len(queries),'Avg Recall: ', recall/len(queries))
