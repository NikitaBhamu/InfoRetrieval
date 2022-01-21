import json
from math import tan
import re
from nltk.stem import PorterStemmer
from rank_bm25 import BM25Okapi
from rake_nltk import Rake
import numpy as np
from evaluate import *
rake_nltk_var = Rake()

porter = PorterStemmer()
def getTerms(text):
    terms = []
    text = text.lower()
    words = re.split(r'[\n`;\-,\s.>?:"\'\[\](){}@#+!_~&*%^=|$/<>]\s*', text)
    #words = word_tokenize(review)
    for word in words:
        if word!='':
            terms.append(porter.stem(word))
    return terms

def getCollectionData():
    print("GENERATING CORPUS")
    corpusmap = {}
    corpus = {}
    with open('../data/all_blocks2.txt') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            passage = json.loads(line)
            #print(passage, file=out)
            corpusmap[i]=passage["id"]
            corpus[i]=passage["text"]
            print("blocks: ", i)
            if i==10000: break
    # print(json.dumps(corpusmap, indent=4), file=open('../stored/corpusmaphalfmntitle.json', 'w+'))
    # print(json.dumps(corpus, indent=4), file=open('../stored/corpussmallhalfmntitle.json', 'w+'))
    return corpusmap, corpus


def getQueriesHist(filename='../data/CANARD_Release/train.json'):
    queries = {}
    his_query = {}
    traindata = json.load(open(filename))
    for i, conversation in enumerate(traindata):
        #if(i+1 < len(traindata) and traindata[i+1]['Question_no']==1):
        qid = conversation["QuAC_dialog_id"]+'@'+str(conversation["Question_no"])
        history = " ".join(conversation["History"])
        rake_nltk_var.extract_keywords_from_text(history)
        keyword_extracted = rake_nltk_var.get_ranked_phrases()
        queries[qid] = keyword_extracted[0] + ' ' +conversation["Question"]
        his_query[qid] = (conversation["History"],conversation["Question"])
        #if(i==5): break
    return queries

def getQueries(filename='../data/CANARD_Release/train.json'):
    queries = {}
    traindata = json.load(open(filename))
    for i, conversation in enumerate(traindata):
        #if(i+1 < len(traindata) and traindata[i+1]['Question_no']==1):
        qid = conversation["QuAC_dialog_id"]+'@'+str(conversation["Question_no"])
        queries[qid] = conversation["Question"]
        if(i==100): break
    return queries

def getIdealQueries(filename='../data/CANARD_Release/train.json'):
    queries = {}
    traindata = json.load(open(filename))
    for i, conversation in enumerate(traindata):
        #if(i+1 < len(traindata) and traindata[i+1]['Question_no']==1):
        qid = conversation["QuAC_dialog_id"]+'@'+str(conversation["Question_no"])
        queries[qid] = conversation["Rewrite"]
        if(i==100): break
    return queries

def rankBM25(corpus, queries, k):
    corpuslist = list(corpus.values())
    corpuslist = [doc.split(" ") for doc in corpuslist]
    bm25 = BM25Okapi(corpuslist)
    rankedDocs = {}
    i = 0
    l = len(queries)
    for qid in queries:
        # print(qid, i, l)
        i+=1
        query = (queries[qid]).split(' ')
        doc_scores = bm25.get_scores(query)
        indices = np.argpartition(doc_scores, -1*k)[-1*k:]
        indices = indices[np.argsort(doc_scores[indices])]
        indices = [indices[len(indices)-1-k] for k in range(len(indices))]
        rankedDocs[qid]=[corpusmap[index] for index in indices]
    return rankedDocs

corpusmap, corpus = getCollectionData()
queries = getQueries()
ranked_queries = rankBM25(corpus, queries, 10)
queriesId = getIdealQueries()
topDocs_queries = rankBM25(corpus, queriesId, 20)

evaluate(ranked_queries, topDocs_queries, queries, len(corpus))

queries = getQueriesHist()
ranked_queries = rankBM25(corpus, queries, 10)

evaluate(ranked_queries, topDocs_queries, queries, len(corpus))
