from bs4 import BeautifulSoup
from stemmer import *
from invidx_cons import *
import re
import sys
import os
import json


def intersection_of_2_lst(l1,l2):
    lst = []
    i=0
    j=0
    if(len(l1)==0 or len(l2)==0):
        return lst
    else:
        while(i<len(l1) and j<len(l2)):
            if(l1[i] == l2[j]):
                lst.append(l1[i])
                i += 1
                j += 1
            elif(l1[i]<l2[j]):
                i += 1
            else:
                j += 1
        return lst


def intersection_of_lst(listt):
    for i in range(1,len(listt)):
        lst = intersection_of_2_lst(listt[i-1],listt[i])
        listt[i] = lst
    return listt[len(listt)-1]
     
     
def query_search(queryfilepath, resultfilepath, indexfilepath, dictfilepath):
    queryfile = open(queryfilepath,'r')
    resultfile = open(resultfilepath,'w')
    querynum = -1
    
    dictfile = open(dictfilepath,'r')
    dictfiledata = json.load(dictfile)
    Documentinfo = dictfiledata["Documents"]
    Dictionary = dictfiledata["Dictionary"]
    Compression = dictfiledata["Compression"]
    Stopwords = dictfiledata["Stopwords"]
    
    if(int(dictfiledata["Compression"]["id"]) == 3):
        decodeC3(dictfilepath, indexfilepath)
        indexfilepath = "newindexfile.idx"
    
    k = -1
    if(int(dictfiledata["Compression"]["id"]) == 4):
        k = int(dictfiledata["k"])
        
    indexfile = open(indexfilepath,"rb")
    p = PorterStemmer()
    
    while True:
        line = queryfile.readline()
        if not line:
            break
        querynum += 1
        result = query_result(line, indexfile, p, Documentinfo, Compression, Dictionary, Stopwords, k)
        if(len(result)==0):
            pass
        else:
            for r in result:
                resultfile.write("Q"+str(querynum)+ " " + str(r) + " " + "1.0\n")
                
    dictfile.close()
    indexfile.close()
    if(int(dictfiledata["Compression"]["id"]) == 3):
        os.remove(indexfilepath)

def query_result(query, indexfile, p, Documentinfo, compression, Dictionary, Stopwords, k):
    
    compression_technique = compression["id"]
    
    split_at = ' |,|\.|:|\`|;|"|\'|\[|\]|\(|\)|\{|\}|\\n'
    res = re.split(split_at,query)
    lst = []
    
    if(int(compression_technique)==0):
        for r in res:
            word = p.stem(r.lower(), 0,len(r)-1)
            if(word != "" and (Stopwords.get(word)==None)):
                l = decodeC0(Dictionary, indexfile, word)
                lst.append(l)
    
    elif(int(compression_technique)==1):
        for r in res:
            word = p.stem(r.lower(), 0,len(r)-1)
            if(word != "" and (Stopwords.get(word)==None)):
                l = decodeC1(Dictionary, indexfile, word)
                lst.append(l)
    
    elif(int(compression_technique)==2):
        for r in res:
            word = p.stem(r.lower(), 0,len(r)-1)
            if(word != "" and (Stopwords.get(word)==None)):
                l = decodeC2(Dictionary, indexfile, word)
                lst.append(l)
    
    elif(int(compression_technique)==3):
        for r in res:
            word = p.stem(r.lower(), 0,len(r)-1)
            if(word != "" and (Stopwords.get(word)==None)):
                l = decodeC0(Dictionary, indexfile, word)
                lst.append(l)
    elif(int(compression_technique)==4):
        for r in res:
            word = p.stem(r.lower(), 0,len(r)-1)
            if(word != "" and (Stopwords.get(word)==None)):
                l = decodeC4(Dictionary, indexfile, word, k)
                lst.append(l)
    else:
        pass
    
    #print(lst)
    result_list = intersection_of_lst(lst)
    #print(result_list)
    result_str_list = []
    for rl in result_list:
        result_str_list.append(Documentinfo[str(rl)])
    return result_str_list
    
#DECODE IS ALSO NOT IMPLEMENTED

if __name__ == '__main__':
    
    argumentlist = sys.argv
    queryfilepath = argumentlist[1]
    resultfilepath = argumentlist[2]
    indexfilepath = argumentlist[3]
    dictfilepath = argumentlist[4]
    
    query_search(queryfilepath, resultfilepath, indexfilepath, dictfilepath)
        
    
