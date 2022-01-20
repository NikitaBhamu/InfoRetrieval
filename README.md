# InfoRetrieval
This folder contains the assignment of the course COL764 : "Information Retrieval and Web Search".

## Assignment 1  :  Inverted Index Construction
In this assignment the goal was to build an efficient boolean retrieval system for English corpora.<br />
1) The documents in the corpora are in the XML fragment form. The document collection is first inverted and an on-disk inverted index is built, consisting of a dictionary file and a single file of all postings lists.<br />
2) Then to make the storage efficient 4 different postings list compression models are implemented and corresponding to that the decompression model of each of them.<br />
3) The system then responds to both the Single keyword retrieval and Multi-keyword retrieval efficiently.<br />

## Assignment 2  :  Prior Ranking of Documents
The goal of this assignment is to simply compute prior similarity-based authority of documents and qualitatively analyse the results. 
1) First the similarity graph between each pair of documents in the collection (the famous "20news-groups" dataset) is computed using two similarity algorithms which are Cosine Similarity and Jaccard Similarity.
2) Then on this similarity graph, the PageRank scores of all documents is computed using the Scikit-Network module.
