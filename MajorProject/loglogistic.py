import json
import math
import re
from nltk.stem import PorterStemmer
from rank_bm25 import BM25Okapi
from rake_nltk import Rake
import numpy as np
from collections import Counter
from bm25 import *
rake_nltk_var = Rake()



#Function to find the termfrequency map for all the documents and the inverse document frequency map
def tfIdf_preProcess(corpuslist):
    inverse_doc_freq = {}   #vocabulary : doc frequency
    term_freq = {}   #doc : term_frequency map
    doc_length = {}
    num_docs = 0
    for doc in corpuslist:
        num_docs += 1
        doc_length[num_docs] = len(doc)
        docTerm_freq = {}
        for word in doc:
            if(word == " " or word == "" ):
                continue
            else:
                #word = p.stem(word.lower(), 0,len(word)-1)
                if(docTerm_freq.get(word) == None):
                    docTerm_freq[word] = 1
                    if(inverse_doc_freq.get(word) == None):
                        inverse_doc_freq[word] = 1
                    else:
                        inverse_doc_freq[word] += 1
                else:
                    docTerm_freq[word] += 1
        term_freq[num_docs] = docTerm_freq
    return inverse_doc_freq, term_freq, num_docs, doc_length


def query_freq_mapfun(queries):
    query_freq_map = {}
    for qid in queries:
        query = (queries[qid]).split(' ')
        query_map = {}
        for word in query:
            if(word == " " or word == "" ):
                continue
            else:
                if(query_map.get(word) == None):
                    query_map[word] = 1
                else:
                    query_map[word] += 1
        query_freq_map[qid] = query_map
    return query_freq_map


def rankll(corpus, queries, k):
    #Pichle wale code se we will get corpusmap, corpus, and generated queries
    #number : docid
    #number : doctext
    #id : querystring
    corpuslist = list(corpus.values())
    corpuslist = [doc.split(" ") for doc in corpuslist]

    inverse_doc_freq, term_freq, total_num_docs, doc_length = tfIdf_preProcess(corpuslist)

    query_freq_map = query_freq_mapfun(queries)
    avdl = 0
    for d in doc_length:
        avdl += doc_length[d]
    avdl = avdl/total_num_docs

    qid_doc_rank = {}
    for qid in query_freq_map:
        print(qid)
        q_map = query_freq_map[qid]
        rankofDocs = {}
        for d in doc_length:
            length_doc = doc_length[d]
            freq_doc = term_freq[d]
            score = 0
            for term in q_map:
                count_w_Q = q_map[term]
                tf_w_D = freq_doc.get(term,0) * math.log(1+avdl/length_doc)
                lambda_w = inverse_doc_freq.get(term,0)/total_num_docs
                score += count_w_Q * math.log((tf_w_D+1+lambda_w)/(lambda_w+1))
            rankofDocs[d] = score
        rankofDocs = sorted(rankofDocs, key = lambda i: rankofDocs[i], reverse=True)
        qid_doc_rank[qid] = rankofDocs
        qid_doc_rank[qid]=[corpusmap[index-1] for index in rankofDocs][:k]
    return qid_doc_rank

traindata = json.load(open('../data/CANARD_Release/train.json'))
queries, his_query = getQueries()
queriesId = getIdealQueries()
ranked_queries = rankll(corpus, queries, 20)
topDocs_queries = rankBM25(corpus, queriesId, 20)
evaluate(ranked_queries, topDocs_queries, queries, len(corpus))
