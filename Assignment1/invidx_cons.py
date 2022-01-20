from bs4 import BeautifulSoup
from stemmer import *
import re
import sys
import os
import json
import math


def decodeC0( dictionary, postlist, search_term ):
    #dict = open(dictpath,"r")
    #postlist = open(postlistpath,"rb")
    #data = json.load(dict)

    #dictionary = data["Dictionary"]

    lst = []
    #print(search_term , end = " ")
    search_result = dictionary.get(search_term)
    if(search_result == None):
        return lst
    else:
        offset = int(search_result[0])
        docs = int(search_result[1])
        postlist.seek(offset)
        docread = 0
        while( docread != docs):
            docid = postlist.read(4)
            docno = int.from_bytes(docid,'big')
            #print(str(docno), end = " ")
            lst.append(docno)
            docread += 1
        #print("\n")
        return lst


#COMPRESSION STRATEGY 1
def compressed_strC1(s,req_bytes):
    str = ""
    i = len(s)-1
    count = 0
    first = 1
    while(i >= 0):
        if(count == 7):
            if(first == 1):
                str = '0'+str
                first = 0
                count = 0
            else:
                str = '1'+str
                count = 0
        str = s[i]+str
        i = i-1
        count += 1

    while(count != 7):
        str = '0'+str
        count += 1

    if(first == 1):
        str = '0'+str
    else:
        str = '1'+str

    lenstr = len(str)
    bytelist = []
    ptr = 0
    while(ptr != lenstr):
        binstr = str[ptr:(ptr+8)]
        k = int(binstr,2)
        binaryk = k.to_bytes(1,byteorder='big')
        ptr += 8
        bytelist.append(binaryk)
    
    return bytelist
    

def compressionC1( dictpath, postlistpath , indexfilename):

    comp_dict = open(indexfilename+".dict", "w")
    comp_postlist = open(indexfilename+".idx", "wb")

    dict = open(dictpath,"r")
    postlist = open(postlistpath,"rb")

    data = json.load(dict)

    prev_dict = data["Dictionary"]
    New_dictionary = {}

    length_covered = 0
    for d in prev_dict:
        prev = 0
        p = prev_dict[d]
        offset = int(p[0])
        docs = int(p[1])
        count = 0
        postlist.seek(offset)
        total_req_bytes = 0
        while(count != docs):
            docid = postlist.read(4)
            docno = int.from_bytes(docid,'big')
            gapencdocno = docno-prev
            prev = docno
            docbin = bin(gapencdocno).replace("0b","")
            req_bytes = math.ceil(len(docbin)/7)
            total_req_bytes += req_bytes
            strtowritelist = compressed_strC1(docbin,req_bytes)
            for l in strtowritelist:
                comp_postlist.write(l)
            count += 1
    
        New_dictionary[d] = (length_covered, docs)
        length_covered += total_req_bytes
        
    DictToDump = {}
    DictToDump["Dictionary"] = New_dictionary
    DictToDump["Documents"] = Documentinfo
    DictToDump["Stopwords"] = stop_words
    DictToDump["Compression"] = Compression
    json.dump(DictToDump, comp_dict)
    
    os.remove(dictpath)
    os.remove(postlistpath)
    comp_dict.close()
    comp_postlist.close()
    

#DECODING OF STRATEGY 1
def decodeC1( dictionary, postlist, search_term ):

    #dict = open(dictpath,"r")
    #postlist = open(postlistpath,"rb")
    #data = json.load(dict)
    #dictionary = data["Dictionary"]
    
    lst = []
    search_result = dictionary.get(search_term)
    #print(search_term , end = " ")
    if(search_result == None):
        return lst
    else:
        offset = int(search_result[0])
        docs = int(search_result[1])
        postlist.seek(offset)
        docread = 0
        docid = ""
        helper = ""
        prev = 0
        while( docread != docs):
            docid = ""
            helper = int.from_bytes(postlist.read(1),'big')
            while(helper >= 256):
                usefulint = helper-256
                docid = docid + '{0:07b}'.format(usefulint)
                helper = int.from_bytes(postlist.read(1),'big')
            docid = docid + '{0:07b}'.format(helper)
            docno = int(docid,2)+prev
            prev = docno
            lst.append(docno)
            #print(str(docno), end = " ")
            docread += 1
        #print("\n")
        return lst

#COMPRESSION STRATEGY 2
def compressed_strC2(x):
    str = ""
    bin_x = bin(x).replace("0b","")
    lx = len(bin_x)
    bin_lx = bin(lx).replace("0b","")
    llx = len(bin_lx)
    U_llx = ""
    for i in range(1,llx):
        U_llx += '1'
    U_llx += '0'
    lsb_lx = bin_lx[1:]
    lsb_x = bin_x[1:]
    
    str = U_llx + lsb_lx + lsb_x
    l = len(str)
    
    bytes_in_str = 0
   
    if(l%8 == 0):
        bytes_in_str = l//8
    else:
        for i in range(l%8, 8):
            str += str+'0'
        bytes_in_str = (l//8)+1
    
    ptr = 0
    bytelist = []
    while( ptr != 8*bytes_in_str):
        binstr = str[ptr:ptr+8]
        binvalue = int(binstr,2)
        bytelist.append(binvalue.to_bytes(1,'big'))
        ptr += 8
    
    return (bytelist,bytes_in_str)


def compressionC2( dictpath, postlistpath , indexfilename):
    comp_dict = open(indexfilename+".dict", "w")
    comp_postlist = open(indexfilename+".idx", "wb")

    dict = open(dictpath,"r")
    postlist = open(postlistpath,"rb")

    data = json.load(dict)

    prev_dict = data["Dictionary"]
    New_dictionary = {}

    length_covered = 0
    for d in prev_dict:
        prev = 0
        p = prev_dict[d]
        offset = int(p[0])
        docs = int(p[1])
        count = 0
        postlist.seek(offset)
        total_req_bytes = 0
        while(count != docs):
            docid = postlist.read(4)
            docno = int.from_bytes(docid,'big')+1
            gapencdocno = docno-prev
            prev = docno
    
            bytelist_bytelen = compressed_strC2(gapencdocno)
            bytelist = bytelist_bytelen[0]
            total_req_bytes += int(bytelist_bytelen[1])
            
            for b in bytelist:
                comp_postlist.write(b)
            count += 1
            
        New_dictionary[d] = (length_covered, docs)
        length_covered += total_req_bytes
        
    DictToDump = {}
    DictToDump["Dictionary"] = New_dictionary
    DictToDump["Documents"] = Documentinfo
    DictToDump["Stopwords"] = stop_words
    DictToDump["Compression"] = Compression
    json.dump(DictToDump, comp_dict)
    
    os.remove(dictpath)
    os.remove(postlistpath)
    comp_dict.close()
    comp_postlist.close()

#DECODING OF STRATEGY 2
def process_string(str):
    l = 0
    for i in range(0,len(str)):
        if(str[i]=='1'):
            l += 1
        else:
            l += 1
            break;
    if(l == 0):
        return -1
    else:
        return l
    
    
def decodeC2( dictionary, postlist, search_term ):
    
    lst = []
    search_result = dictionary.get(search_term)
    
    if(search_result == None):
        return lst
    else:
        offset = int(search_result[0])
        docs = int(search_result[1])
        postlist.seek(offset)
        docread = 0
        helper = ""
        prev = -1
        while( docread != docs):
            U_llx = 0
            byte_read = int.from_bytes(postlist.read(1),'big')
            zerofound = process_string('{0:08b}'.format(byte_read))
            while(zerofound == -1):
                U_llx += 8
                byte_read = int.from_bytes(postlist.read(1),'big')
                zerofound = process_string('{0:08b}'.format(byte_read))
            U_llx += zerofound
            str = '{0:08b}'.format(byte_read)
            lx = '1'
            len_covered_lx = 0
           
            ptr = zerofound
            while(len_covered_lx != U_llx-1):
                if(ptr == 8):
                    byte_read = int.from_bytes(postlist.read(1),'big')
                    str = '{0:08b}'.format(byte_read)
                    ptr = 0
                lx = lx + str[ptr]
                ptr += 1
                len_covered_lx += 1
                
            value_lx = int(lx,2)
            x = '1'
            len_covered_x = 0
            while(len_covered_x != value_lx-1):
                if(ptr == 8):
                    byte_read = int.from_bytes(postlist.read(1),'big')
                    str = '{0:08b}'.format(byte_read)
                    ptr = 0
                x = x + str[ptr]
                ptr += 1
                len_covered_x += 1
                
            value_x = int(x,2)
            docno = value_x+prev
            prev = docno
            lst.append(docno)
            docread += 1
        return lst
     

#COMPRESSION STRATEGY 3

def decodeC3( dictpath, postlistpath):
    os.system('python -m snappy -d '+ postlistpath + ' ' + 'newindexfile.idx')


def compressionC3(dictpath, postlistpath, indexfilename):
    prevdictfile = open(dictpath, 'r')
    data = json.load(prevdictfile)
    
    newidxfilepath = indexfilename+'.idx'
    newdictfile = open(indexfilename+'.dict', 'w')
    
    os.system('python -m snappy -c '+ postlistpath +' '+ newidxfilepath)
    
    DictToDump = {}
    DictToDump["Dictionary"] = data["Dictionary"]
    DictToDump["Documents"] = data["Documents"]
    DictToDump["Stopwords"] = data["Stopwords"]
    DictToDump["Compression"] = data["Compression"]
    json.dump(DictToDump, newdictfile)
    
    os.remove(dictpath)
    os.remove(postlistpath)
    newdictfile.close()


#COMPRESSION STRATEGY 4

def compressed_strC4(x, value_k):
    k = value_k
    b = pow(2,k)
    q = math.floor((x-1)/b)
    r = x - (q*b) - 1
    C_r = bin(r).replace("0b","")
    
    lenCr = len(C_r)
    for i in range(lenCr, k):
        C_r = '0'+C_r
    
    U_q_plus_1 = ""
    for i in range(1,q+1):
        U_q_plus_1 += '1'
    U_q_plus_1 += '0'
    
    binstr = U_q_plus_1 + C_r
    l = len(binstr)
    
    req_bytes = 0
    if(l%8 == 0):
        req_bytes += l//8
    else:
        req_bytes += l//8
        for i in range(l%8,8):
            binstr += '0'
        req_bytes += 1
    
    byte_list = []
    ptr = 0
    while(ptr != req_bytes*8):
        s = binstr[ptr:(ptr+8)]
        s_value = int(s,2)
        byte_list.append(s_value.to_bytes(1,'big'))
        ptr += 8
    
    return (byte_list, req_bytes)
    

def compressionC4( dictpath, postlistpath , indexfilename, value_k):
    comp_dict = open(indexfilename+".dict", "w")
    comp_postlist = open(indexfilename+".idx", "wb")

    dict = open(dictpath,"r")
    postlist = open(postlistpath,"rb")

    data = json.load(dict)

    prev_dict = data["Dictionary"]
    New_dictionary = {}

    length_covered = 0
    for d in prev_dict:
        prev = 0
        p = prev_dict[d]
        offset = int(p[0])
        docs = int(p[1])
        count = 0
        postlist.seek(offset)
        total_req_bytes = 0
        while(count != docs):
            docid = postlist.read(4)
            docno = int.from_bytes(docid,'big')+1
            gapencdocno = docno-prev
            prev = docno

            bytelist_bytelen = compressed_strC4(gapencdocno, value_k)
            bytelist = bytelist_bytelen[0]
            total_req_bytes += int(bytelist_bytelen[1])
            
            for b in bytelist:
                comp_postlist.write(b)
            count += 1
            
        New_dictionary[d] = (length_covered, docs)
        length_covered += total_req_bytes
        
    DictToDump = {}
    DictToDump["Dictionary"] = New_dictionary
    DictToDump["Documents"] = Documentinfo
    DictToDump["Stopwords"] = stop_words
    DictToDump["Compression"] = Compression
    DictToDump["k"] = value_k
    json.dump(DictToDump, comp_dict)

    os.remove(dictpath)
    os.remove(postlistpath)
    comp_dict.close()
    comp_postlist.close()


def decodeC4( dictionary, postlist, search_term, value_k):
    
    k = value_k
    b = pow(2,k)
    
    lst = []
    search_result = dictionary.get(search_term)
            
    if(search_result == None):
        return lst
    else:
        offset = int(search_result[0])
        docs = int(search_result[1])
        postlist.seek(offset)
        docread = 0
        helper = ""
        prev = -1
        while( docread != docs):
            U_q_plus_1 = 0
            byte_read = int.from_bytes(postlist.read(1),'big')
            zerofound = process_string('{0:08b}'.format(byte_read))
            while(zerofound == -1):
                U_q_plus_1 += 8
                byte_read = int.from_bytes(postlist.read(1),'big')
                zerofound = process_string('{0:08b}'.format(byte_read))
            U_q_plus_1 += zerofound
            value_q = U_q_plus_1 - 1
            
            str = '{0:08b}'.format(byte_read)
            r = ''
            len_covered_r = 0
            ptr = zerofound
            while(len_covered_r != k):
                if(ptr == 8):
                    byte_read = int.from_bytes(postlist.read(1),'big')
                    str = '{0:08b}'.format(byte_read)
                    ptr = 0
                r = r + str[ptr]
                ptr += 1
                len_covered_r += 1
                        
            value_r = int(r,2)
            value_x = value_r + (value_q * b) + 1
            docno = value_x + prev
            prev = docno
            lst.append(docno)
            docread += 1
        return lst
             

def write_to_file(dict,filenum, FinalDictMap):
     indexfilename = "./FilestoMerge/storeindex"+str(filenum)+".idx"
     f = open(indexfilename,"wb")
     length_covered = 0
     for i in sorted(dict):
         termtriplet = FinalDictMap.get(i)
         if(termtriplet == None):
            lst = []
            lst.append((filenum, length_covered, len(dict[i])))
            FinalDictMap[i] = lst
         else:
            termtriplet.append((filenum, length_covered, len(dict[i])))

         length_covered += len(dict[i])*4
         for j in dict[i]:
            bin = j.to_bytes(4,byteorder="big")
            f.write(bin)
  
  
            
def final_merge(FinalDictMap, filenum, indexfilename, Documentinfo, stop_words, Compression ):
    if(int(Compression["id"])==0):
        filename1 = indexfilename+".dict"
        filename2 = indexfilename+".idx"
        f1 = open(filename1,"w")
        f2 = open(filename2,"wb")
        postlistfiles = []
        for j in range(0,filenum+1):
            f = open("./FilestoMerge/storeindex"+str(j)+".idx", "rb")
            postlistfiles.append(f)
                    
        length_covered = 0
        docaddition = 0
        Dictionary = {}
        for i in sorted (FinalDictMap):
            total_docs = 0
            for t in FinalDictMap[i]:
                fileno = int(t[0])
                offset = int(t[1])
                numdocs = int(t[2])
                total_docs += numdocs
                postlistfiles[fileno].seek(offset)
                data = postlistfiles[fileno].read(4*numdocs)
                f2.write(data)
            Dictionary[i] = (length_covered, total_docs)
            length_covered += total_docs * 4
        
        DictToDump = {}
        DictToDump["Dictionary"] = Dictionary
        DictToDump["Documents"] = Documentinfo
        DictToDump["Stopwords"] = stop_words
        DictToDump["Compression"] = Compression
        json.dump(DictToDump, f1)
        
        f1.close()
        f2.close()
        
    elif(int(Compression["id"])==1 or int(Compression["id"])==2 or int(Compression["id"])==3 or int(Compression["id"])==4):
    
        filename1 = indexfilename+"helper.dict"
        filename2 = indexfilename+"helper.idx"
        f1 = open(filename1,"w")
        f2 = open(filename2,"wb")
        postlistfiles = []
        for j in range(0,filenum+1):
            f = open("./FilestoMerge/storeindex"+str(j)+".idx", "rb")
            postlistfiles.append(f)
                    
        length_covered = 0
        docaddition = 0
        Dictionary = {}
        for i in sorted (FinalDictMap):
            total_docs = 0
            for t in FinalDictMap[i]:
                fileno = int(t[0])
                offset = int(t[1])
                numdocs = int(t[2])
                total_docs += numdocs
                postlistfiles[fileno].seek(offset)
                data = postlistfiles[fileno].read(4*numdocs)
                f2.write(data)
            Dictionary[i] = (length_covered, total_docs)
            length_covered += total_docs * 4

        DictToDump = {}
        DictToDump["Dictionary"] = Dictionary
        DictToDump["Documents"] = Documentinfo
        DictToDump["Stopwords"] = stop_words
        DictToDump["Compression"] = Compression
        json.dump(DictToDump, f1)
        
        f1.close()
        f2.close()
        
        if(int(Compression["id"])==1):
            compressionC1( indexfilename+"helper.dict", indexfilename+"helper.idx" , indexfilename)
        elif(int(Compression["id"])==2):
            compressionC2( indexfilename+"helper.dict", indexfilename+"helper.idx" , indexfilename)
        elif(int(Compression["id"])==3):
            compressionC3( indexfilename+"helper.dict", indexfilename+"helper.idx" , indexfilename)
        else:
            k = 6
            compressionC4( indexfilename+"helper.dict", indexfilename+"helper.idx" , indexfilename, k)
        
    else:
        print("not implemented\n")
        
    
def helperfunction1():
    dictpath = "indexfilehelper.dict"
    #print("BYEEE")
    postlistpath = "indexfilehelper.idx"
    f = open(dictpath,'r')
    data = json.load(f)

    dictionary = data["Dictionary"]
    postlist = open(postlistpath, "rb")
    
    resultfile = open("resultC1.txt", "w+")
    print("C1")
    for d in dictionary:
        lst = decodeC0( dictionary, postlist, d)
        lststr = ""
        for l in lst:
            lststr += str(l)+" "
        resultfile.write(d + " " + lststr+"\n")
        print(d + " " + lststr)
        
def helperfunction4():
    dictpath = "indexfile.dict"
    postlistpath = "indexfile.idx"
    f = open(dictpath,'r')
    data = json.load(f)
    dictionary = data["Dictionary"]
    postlist = open(postlistpath, "rb")
    
    resultfile = open("resultC4.txt", "w+")
    k = int(data["k"])
    print("C4")
    for d in dictionary:
        lst = decodeC4( dictionary, postlist, d, k)
        lststr = ""
        for l in lst:
            lststr += str(l)+" "
        resultfile.write(d + " " + lststr+"\n")
        print(d + " " + lststr)
            
def helperfunction2():
    dictpath = "indexfile.dict"
    postlistpath = "indexfile.idx"
    f = open(dictpath,'r')
    data = json.load(f)
    dictionary = data["Dictionary"]
    
    resultfile = open("resultC2.txt", "w+")
    
    for d in dictionary:
        lst = decodeC1( dictpath, postlistpath, d)
        lststr = ""
        for l in lst:
            lststr += str(l)+" "
        resultfile.write(d + " " + lststr+"\n")


def helperfunction3():
    dictpath = "indexfile.dict"
    postlistpath = "indexfile.idx"
    f = open(dictpath,'r')
    data = json.load(f)
    dictionary = data["Dictionary"]
    
    resultfile = open("resultC3.txt", "w+")
    
    for d in dictionary:
        lst = decodeC2( dictpath, postlistpath, d)
        lststr = ""
        for l in lst:
            lststr += str(l)+" "
        resultfile.write(d + " " + lststr+"\n")


def clean(filenum):
    for i in range(0,filenum+1):
        os.remove("./FilestoMerge/storeindex"+str(i)+".idx")
    os.rmdir("./FilestoMerge")


if __name__ == '__main__':
    
    #thresold to copy contents from memory to disc
    MaxSize = 1500000000
    #MaxSize = 150

    #directory creation for the forming of new files in it
    cwd = os.getcwd()
    directory = "FilestoMerge"
    path = os.path.join(cwd,directory)
    
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        for f in os.listdir(path):
            os.remove(os.path.join(path,f))

    #object which stems words
    p = PorterStemmer()

    #to read and store the indexable xml tags
    argumentList = sys.argv
    
    document_collectionpath = argumentList[1]
    
    indexfilename = argumentList[2]
    
    #stop-word list provided
    stop_words = {}
    stop_word_file = open(argumentList[3],'r')
    for line in stop_word_file:
        for word in line.split():
            stop_words[word] = True
            
    compression_technique = argumentList[4]
    Compression = {}
    Compression["id"] = compression_technique
    
    xml_tags = []
    xml_tag_file = open(argumentList[5],'r')
    for line in xml_tag_file:
        xml_tags.append(line.strip())


    #current size of memory
    size = 0
    filenum = 0
    documentnum = 0
    Documentinfo = {}

    split_at = ' |,|\.|:|\`|;|"|\'|\[|\]|\(|\)|\{|\}|\\n'
    Dict = {}

    #File which stores the temporary dictionary
    FinalDictMap = {}

    #path of the directory
    for file in os.listdir(document_collectionpath):

        if(size > MaxSize):
            write_to_file(Dict,filenum,FinalDictMap)
            filenum += 1
            size = 0
            Dict = {}
        
        data = []
        if(file[0] != '.'):
            with open(os.path.join(document_collectionpath, file) ,'r') as f:
                data = f.readlines()
                data = "".join(data)
                contents = "<FILE>\n" + data + "\n</FILE>"
            
                soup = BeautifulSoup(contents,'xml')

                documents = soup.find_all('DOC')

                #storing the keys and values in the python dictionary
                for d in documents:
                    docid = d.find(xml_tags[0]).get_text().strip()
                    Documentinfo[documentnum] = docid
                    docno = documentnum
                    documentnum += 1
                    Terms_encounterd = {}
                    for i in range(1,len(xml_tags)):
                        text = d.find_all(xml_tags[i])
                        for t in text:
                            res = re.split(split_at,t.get_text())
                            for r in res:
                                if(r != ""):
                                    if(stop_words.get(r.lower()) == None):
                                        word = p.stem(r.lower(), 0,len(r)-1)
                                        is_term_encountered = Terms_encounterd.get(word)
                                        if(is_term_encountered == None):
                                            dclst = Dict.get(word)
                                            if(dclst == None):
                                                doclist = []
                                                doclist.append(docno)
                                                size += 1
                                                Dict[word] = doclist
                                                Terms_encounterd[word] = True
                                            else:
                                                dclst.append(docno)
                                                size += 1
                                                Terms_encounterd[word] = True
            
    #print("Total documents : "+str(documentnum))
    write_to_file(Dict,filenum,FinalDictMap)
    final_merge(FinalDictMap, filenum, indexfilename, Documentinfo, stop_words, Compression)
    clean(filenum)
    
    
