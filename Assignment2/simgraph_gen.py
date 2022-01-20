from bs4 import BeautifulSoup
from stemmer import *
import re
import sys
import os
import json
import math
import numpy as np
import networkx as nx
import sknetwork as skn
from sknetwork.utils import edgelist2adjacency
from sknetwork.ranking import PageRank



split_at = ' |,|\.|:|\`|;|"|\'|\[|\]|\(|\)|\{|\}|\\n|>|<|$|@'

p = PorterStemmer()

#NEWLY ADDED FUNCTION
def tokenise(string):
    delimiters = [' ',",",".",":",";","'","\"","@","#","+","!","_","~","&","*","%","^","=","`","|","$","\n","(",")",">","<"]
    for d in delimiters:
        string = string.replace(d," ")
    return string.split()

#Function to find the termset of the document
def find_termset(doc):
    termset = set()
    with open(doc,'r',encoding='utf-8', errors='ignore') as f:
        #print(doc)
        #print("############")
        data = f.readlines()
        data = "".join(data)
    res = tokenise(data.strip())
    for word in res:
        if(word == " " or word == "" ):
            continue
        else:
             word = p.stem(word.lower(), 0,len(word)-1)
             termset.add(word)
    return termset
 
#Function to find the similariy between the pairs of the document using Jaccard method
def SimM1(filenames):
    #Term Sets of all the files
    TermSets = []
    #i = 1
    for f in filenames:
        TermSets.append(find_termset(f))
          
    #Map having (doc1,doc2):Similarity
    Similarity = {}
    #Iterating through the filenames
    for i in range(0, len(filenames)):
        doc1 = filenames[i]
        if(doc1[0] != '.'):
            TermSetdoc1 = TermSets[i]
            for j in range(i+1, len(filenames)):
                doc2 = filenames[j]
                if(doc2[0] != '.'):
                    TermSetdoc2 = TermSets[j]
                    TermSetUnion = TermSetdoc1.union(TermSetdoc2)
                    TermSetInter = TermSetdoc1.intersection(TermSetdoc2)
                    frac = len(TermSetInter)/len(TermSetUnion)
                    Similarity[(doc1,doc2)] = '%.4f'%frac
                else:
                    continue
        else:
            continue
    return Similarity
     
#########################################################################################################

#Function to find the termfrequency map for all the documents and the inverse document frequency map
def tfIdf_preProcess(filenames):
    inverse_doc_freq = {}   #vocabulary : doc frequency
    term_freq = {}   #doc : term_frequency map
    num_docs = 0
    for doc in filenames:
        num_docs += 1
        docTerm_freq = {}
        with open(doc,'r',encoding='utf-8', errors='ignore') as f:
            data = f.readlines()
            data = "".join(data)
            res = tokenise(data.strip())
            for word in res:
                if(word == " " or word == "" ):
                    continue
                else:
                     word = p.stem(word.lower(), 0,len(word)-1)
                     if(docTerm_freq.get(word) == None):
                        docTerm_freq[word] = 1
                        if(inverse_doc_freq.get(word) == None):
                            inverse_doc_freq[word] = 1
                        else:
                            inverse_doc_freq[word] += 1
                     else:
                        docTerm_freq[word] += 1
        term_freq[doc] = docTerm_freq
    return inverse_doc_freq, term_freq, num_docs
    
#Finding the magnotude of the tf-idf map of a document
def Magnitude(mp):
    mag = 0
    for w in mp:
      mag += mp[w]*mp[w]
    return math.sqrt(mag)

#Finding the dot product of the tf-idf maps of two documents
def DotProduct(mp1,mp2):
    pdt = 0
    for w in mp1:
        if(mp2.get(w) != None):
            pdt += mp1[w]*mp2[w]
    return pdt
    
#Function to find the similariy between the pairs of the document using Cosine method
def SimM2(filenames):
    inverse_doc_freq, term_freq, num_docs = tfIdf_preProcess(filenames)
    #Tf-idf maps of all the files
    TfIdfMaps = []
    totaldocsread = 0
    for f in filenames:
        totaldocsread += 1
        docTfIdf_Map = term_freq[f]
        #docVec = []
        for w in docTfIdf_Map:
            tf = docTfIdf_Map[w]
            idf = math.log2(1 + num_docs/inverse_doc_freq[w])
            docTfIdf_Map[w] = tf*idf
        TfIdfMaps.append(docTfIdf_Map)
        #print(str(totaldocsread)+ " : "+ f)
        
    MagnitudeMap = []
    for i in range(0, len(filenames)):
        doc = filenames[i]
        docMap = TfIdfMaps[i]
        MagnitudeMap.append(Magnitude(docMap))
        
    #print("THE TOTAL NUM OF DOCS READ ARE : "+str(totaldocsread))
    #print("Similarity loop started")
    docfound = 0
    #Map having (doc1,doc2):Similarity
    Similarity = {}
    for i in range(0, len(filenames)):
        doc1 = filenames[i]
        if(doc1[0] != '.'):
            doc1Map = TfIdfMaps[i]
            doc1Mag = MagnitudeMap[i]
            for j in range(i+1, len(filenames)):
                doc2 = filenames[j]
                if(doc2[0] != '.'):
                    docfound += 1
                    doc2Map = TfIdfMaps[j]
                    doc2Mag = MagnitudeMap[j]
                    frac = (DotProduct(doc1Map,doc2Map))/(doc1Mag*doc2Mag)
                    Similarity[(doc1,doc2)] = '%.4f'%frac
                    #print(docfound)
                else:
                    continue
        else:
            continue
    #print("Similarity loop ended")
    return Similarity
    
#Driving function which decides the similarity function to call and the write the similarity output in a file
def Sim(filenames, method, output_file):
    if(method == "jaccard"):
        simil = SimM1(filenames)
        with open(output_file,'w') as f:
            for s in simil:
                if(float(simil[s]) == 0):
                    continue
                else:
                    doc1 = s[0].split("/")
                    doc1name = doc1[-2]+"/"+doc1[-1]
                    doc2 = s[1].split("/")
                    doc2name = doc2[-2]+"/"+doc2[-1]
                    f.write(doc1name+" "+doc2name+" "+str(simil[s])+"\n")
        return simil
                
    else:
         simil = SimM2(filenames)
         with open(output_file,'w') as f:
             for s in simil:
                if(float(simil[s]) == 0):
                    continue
                else:
                    doc1 = s[0].split("/")
                    doc1name = doc1[-2]+"/"+doc1[-1]
                    doc2 = s[1].split("/")
                    doc2name = doc2[-2]+"/"+doc2[-1]
                    f.write(doc1name+" "+doc2name+" "+str(simil[s])+"\n")
         return simil

#########################################################################################################

#EXTRA UNUSED FUNCTIONS (ONLY USED AT THE TIME OF TESTING)
def listToString(s):
    str1 = " "
    return (str1.join(map(str, s)))
        
def SimHelper(filenames, method, output_file):
    if(method == "jaccard"):
        simil = SimM1(filenames)
        return simil
    else:
        simil = SimM2(filenames)
        return simil

def print_top_40(pr, output_file):
    with open(output_file,'w') as f:
       entries = 0
       for s in sorted(pr.items(), key = lambda kv:(kv[1], kv[0]), reverse=True):
           if(entries == 40):
               break
           else:
               entries += 1
               doc1 = s[0].split("/",1)
               doc1name = doc1[1]
               f.write(doc1name+" "+'%.3f'%s[1]+"\n")


def page_scores(outfile, filenames):
    #print("CAME HERE")
    Similarity = {}
    with open(outfile,'r') as f:
        lines = f.readlines()
        print(type(lines))
        for line in lines:
            content = line.strip().split(' ')
            Similarity[(content[0],content[1])] = content[2]
    edges = []
    for i in range(0,len(filenames)):
        file1list = filenames[i].split("/")
        file1 = file1list[-2] + "/" + file1list[-1]
        for j in range(i+1, len(filenames)):
            file2list = filenames[j].split("/")
            file2 = file2list[-2] + "/" + file2list[-1]
            s = (file1, file2)
            if(Similarity.get(s) != None):
                if(round(float(Similarity[s]),1) > 0.0):
                    edges.append((i,j,round(float(Similarity[s]),1)))
    graph = edgelist2adjacency(edges, undirected=True)
    #print("###########")
    #print(graph.shape, graph.nnz)
    #print("###########")
    pagerank = PageRank()
    scores = pagerank.fit_transform(graph)
    rankedpages = [(filenames[i], scores[i]) for i in range(len(filenames))]
    rankedpages.sort(key= lambda x: -x[1])
            
    for i in range(20):
        if(i >= len(rankedpages)):
            break
        docname = rankedpages[i][0].split("/",1)[1]
        rank = rankedpages[i][1]
        print(docname+" : "+ str(rank))



#Main Function
if __name__ == '__main__':

    p = PorterStemmer()
    argumentList = sys.argv
    method = argumentList[1]
    document_collectionpath = argumentList[2]
    output_file = argumentList[3]
    
    filenames = []
    for dir in os.listdir(document_collectionpath):
        if not dir.startswith('.'):
            for file in os.listdir(os.path.join(document_collectionpath, dir)):
                if not file.startswith('.'):
                    filenames.append(os.path.join(document_collectionpath, dir, file))
    
    Similarity = Sim(filenames, method, output_file)
    page_scores(output_file, filenames)
    
    
        
    

        
    
