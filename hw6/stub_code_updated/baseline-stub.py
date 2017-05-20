#!/usr/bin/env python
'''
Created on May 14, 2014
@author: reid

Modified on May 21, 2015
'''

import sys, nltk, operator

# Read the file from disk
def read_file(filename):
    fh = open(filename, 'r')
    text = fh.read()
    fh.close()
    
    return text

# The standard NLTK pipeline for POS tagging a document
def get_sentences(text):
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    
    return sentences	

# get bag of words
# breaks sentences into set of tokenized sentences, removing stopwords
def get_bow(tagged_tokens, stopwords):
    return set([t[0].lower() for t in tagged_tokens if t[0].lower() not in stopwords])
	
# searches for similarly tagged tokens and returns them
def find_phrase(tagged_tokens, qbow):
    for i in range(len(tagged_tokens) - 1, 0, -1):
        word = (tagged_tokens[i])[0]
        if word in qbow:
            return tagged_tokens[i+1:]
	
# qtokens: is a list of pos tagged question tokens with SW removed
# sentences: is a list of pos tagged story sentences
# stopwords is a set of stopwords
# matches words to sentences and returns the best answer
def baseline(qbow, sentences, stopwords):
    # Collect all the candidate answers
    answers = []
    for sent in sentences:
        # A list of all the word tokens in the sentence
        sbow = get_bow(sent, stopwords)
        
        # Count the # of overlapping words between the Q and the A
        # & is the set intersection operator
        overlap = len(qbow & sbow)
        print(overlap)
        
        answers.append((overlap, sent))
        
    # Sort the results by the first element of the tuple (i.e., the count)
    # Sort answers from smallest to largest by default, so reverse it
    answers = sorted(answers, key=operator.itemgetter(0), reverse=True)

    # Return the best answer
    best_answer = (answers[0])[1]    
    return best_answer

if __name__ == '__main__':
    text_file = "hw6_dataset/fables-01.sch"
	
    stopwords = set(nltk.corpus.stopwords.words("english"))
    text = read_file(text_file)
    question = "What did the crow feel?"

    # get words for every sentence in sentence
    qbow = get_bow(get_sentences(question)[0], stopwords)
    sentences = get_sentences(text)
	
    answer = baseline(qbow, sentences, stopwords)
	
    print(" ".join(t[0] for t in answer))