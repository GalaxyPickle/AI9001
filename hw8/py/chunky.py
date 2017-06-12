##############
# Alex Lang
# Conor Rogers
#
# HW 6
#
# CHUNKY
#   fetches sentence with the answer contained in it (92%+ accuracy)
##############

import sys, nltk, operator, zipfile, re
from nltk.stem.wordnet import WordNetLemmatizer
import con_parse

# colorssszzzzzz
class c:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# unzip and read story from zip file
def unzip_corpus(input_file, name):
    zip_archive = zipfile.ZipFile(input_file)
    contents = [zip_archive.open(fn, 'r').read().decode('utf-8') 
        for fn in zip_archive.namelist() if fn == name]
    return ''.join(contents)

# get bag of words
# breaks sentences into set of tokenized sentences, removing stopwords
def get_bow(tagged_tokens, stopwords=""):
    if stopwords == "":
        return set([t[0].lower() for t in tagged_tokens])
    else:
        return set([t[0].lower() for t in tagged_tokens if t[0].lower() not in stopwords])

# The standard NLTK pipeline for POS tagging a document
def get_sentences(text):
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    
    return sentences

#returns lemma of word added 
def lemmatizer(tokens):
    lem_tokens = []
    # this little bit is because wordnet lemmas don't play nicely with things verb infinitives....... [very rough fix
    second_form_same_vinfinitive = [('felt','feel'),('fell','fall'),('stood','stand'),('flattered','flatter'),('flattery','flatter')]

    vinfinitive_check = [a for (a,b) in second_form_same_vinfinitive]
    for token in tokens:
        for (a,b) in second_form_same_vinfinitive:
            if a == token:
                lem_tokens += [b]
        if token not in vinfinitive_check:
            lem_tokens += [WordNetLemmatizer().lemmatize(token,'v')]

    return lem_tokens

# qtokens: is a list of pos tagged question tokens with SW removed
# text: list of a list of pos tagged story sentences
# stopwords is a set of stopwords
# matches words to sentences for each text and returns the best answer
def baseline(qbow, text, fnames, stopwords):
    # Collect all the candidate answers
    answers = []
    qbow = set([nltk.LancasterStemmer().stem(word) for word in qbow])
    qbow.update(set(lemmatizer(qbow)))
    # print(qbow)

    i = 0
    for f in text:
        fileN = fnames[i]
        for sent in f:
            # A list of all the word tokens in the sentence
            sbow = get_bow(sent, stopwords)

            # stem all questions and sentences for better results
            sbow = set([nltk.LancasterStemmer().stem(word) for word in sbow])
            sbow.update(set(lemmatizer(sbow)))

            # and then add the other
            # print(sbow)
            
            # Count the # of overlapping words between the Q and the A
            # & is the set intersection operator
            overlap = len(qbow & sbow)
            # print(c.OKGREEN + "overlap: " + c.ENDC + str(overlap))
            
            answers.append((overlap, sent, fileN))

        i += 1
        
    # Sort the results by the first element of the tuple (i.e., the count)
    # Sort answers from smallest to largest by default, so reverse it
    answers = sorted(answers, key=operator.itemgetter(0), reverse=True)
    # print(answers)

    fileN = answers[0][2]
    # print("FILEN NNNNNNNN N N N N N: ", fileN)

    # Return the best answer
    if len(answers) > 0:
        best_answer = (answers[0])[1]
    else:
        best_answer = None

    return best_answer, fileN

# reads file and finds best sentence
def find_best_sentence(question, fnames):
    print(c.OKGREEN)
    print(fnames)

    # raw story / sch
    dataset = "hw8_dataset"
    text = [unzip_corpus(dataset + ".zip", dataset + "/" + f) for f in fnames]

    # get words for every sentence in sentence
    stopwords = set(nltk.corpus.stopwords.words("english"))
    #stopwords = ""

    # get bow for Q
    print("Q: " + c.ENDC + question + c.OKGREEN)
    question = question[:len(question) - 1]
    qbow = get_bow(get_sentences(question)[0], stopwords)
    # print("Q BOW: " + c.ENDC + str(qbow))
    
    # get list of list of POS tag tup sentences in story
    #   [ 
    #   fables-01.story: [sent1: ('the', 'DT'), ...], 
    #       fables-01.sch: [('sack', 'FF'), ...] 
    #   ]
    #   (usually just .story or .sch, not both)
    text = [get_sentences(story) for story in text]

    answer, filename = baseline(qbow, text, fnames, stopwords)
    # print('filename: ', filename)
    if answer != None:
        print(c.OKGREEN + "Answer Sentence: " + c.ENDC + " ".join(t[0] for t in answer))
        answer = [answer]

    qbow = get_sentences(question)[0]

    return answer, qbow, filename

# 1. open story/sch file or both for q
# 2. use super s1ck algorithms to find the best sentence
#   (if story | sch, open both and find best matching sentence)
# 3. return best sentence
def chunk(fnames, question, q_type, q_diff, a):

    # ready storyname to open
    fnames = fnames.split('-')
    fnames = fnames[0] + "-" + fnames[1]

    # ready what kind of storyname to open
    if "|" in q_type:
        q_type = q_type.split('|')
    else:
        q_type = [q_type]
    q_type = [w.strip() for w in q_type]

    fnames = [fnames + '.' + t.lower() for t in q_type]

    answer_sentence, qbow, filename = find_best_sentence(question, fnames)

    answer_sentence = ' '.join(word for word, tag in answer_sentence[0])

    # print("FNAME FNAME: ", fnames[0])

    # print("QUESTION QUESTION: ", question)

    # print("ANSWER SENT ANSWER SENT: ", answer_sentence)

    # print("FILE NAME FILE NAME: ", filename)

    # if answer_sentence == None:
    #     answer = ""
    # else:
    #     answer = chunky_boi.mah_boi(qbow, answer_sentence[0])

    #con_parse.mr_toads_wild_ride("A trapper spread some net in order to catch a big game .","What did the hunter spread?",'fables-06.sch')

    answer = con_parse.mr_toads_wild_ride(answer_sentence, question, filename)

    print(c.OKGREEN + "REAL ANSWER: " + c.ENDC + a)
    print(c.OKGREEN + "Our Answer: " + c.ENDC + answer)


    # if answer == "":
    #     answer = question

    return answer


if __name__ == '__main__':

    # Our tools
    chunker = nltk.RegexpParser(GRAMMAR)
    
    question = "Where was the cheese?"
    fname = 'fables-01.sch'

    answer_sentence = find_best_sentence(question, [fname])
    
    # Extract the candidate locations from these sentences
    locations = find_candidates(answer_sentence, chunker)
    
    # Print them out
    for loc in locations:
        print(loc)
        print(" ".join([token[0] for token in loc.leaves()]))
