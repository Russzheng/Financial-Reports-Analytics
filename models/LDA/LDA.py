# THANKS TO https://www.kaggle.com/c/word2vec-nlp-tutorial/details/part-1-for-beginners-bag-of-words
# for processing the texts, we lower cased every word, reserved only pure alphabets, stemmed the words
# applied stop words, and tokenized texts. quite standard processing
# should be enough as reports are formal writings.

####### I USED TWO MODELS GENSIM AND SKLEARN #######
####### CHECK COMMENTS #######

import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
import os, os.path
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import LatentDirichletAllocation as LDA
import numpy as np
from stemming.porter2 import stem
import matplotlib.pyplot as plt
from scipy.interpolate import spline
from sklearn.pipeline import Pipeline
from gensim import corpora, models
import gensim
import random

DATA_DIR = '/home/peng/Desktop/sentiment_analyses/LDA/data_small'

def load_data(file_name):
    # loading strings and manipulating strings are quite time consuming
    # A LOT file I/O 
    with open(file_name, 'r') as f:
        # remove new lines
        data = f.read().replace('\n', '')
    # lower case
    data = data.lower()
    # remove punctuations and numbers
    data = re.sub("[^a-zA-Z]", " ", data)
    # split to words
    words = data.split()
    # delete stop words like 'the' 'a' and etc.
    # delete company name
    stops = set(stopwords.words("english")) | set(['wells', 'fargo', 'llc']) # use set for speed
    words = [w for w in words if w not in stops]

    # stemming
    words = [stem(word) for word in words]

    #return words ###### GENSIM ######
    return ( " ".join(words)) ###### SKLEARN ######

def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]]))

def plot(topic_li, perplex_li):
    topic_li = np.array(topic_li)
    perplex_li = np.array(perplex_li)

    topic_smooth = np.linspace(topic_li.min(), topic_li.max(), 400)
    per_smooth = spline(topic_li, perplex_li, topic_smooth)

    plt.plot(topic_smooth, per_smooth)
    plt.xlabel('number of topics', fontsize=16)
    plt.ylabel('log(perplexity)', fontsize=16)
    plt.show()

def train_test_split(x, test_pct):
    results = [], []
    for item in x:
        results[0 if random.random() < test_pct else 1].append(item)
    test, train = results
    np.asarray(test)
    np.asarray(train)
    return test, train

def main():
    # how many data entries for our csv files, some double checking
    # prepare bag of words
    print('Dataloading Starts')
    words_li = []
    id_li = []
    for file_name in os.listdir(DATA_DIR):
        id_li.append(file_name)
        words_li.append(load_data(DATA_DIR + '/' + file_name))
   
    data_size = len(id_li)
    print('Data set size is :', data_size)
    # for some really bizzare cases
    if len(words_li) != len(id_li):
        print('ERROR when loading data!')
        exit(9)
    
    np.asarray(words_li)

    ###### GENSIM  ######
    #x_test, x_train = train_test_split(words_li, 0.2)

    #dictionary = corpora.Dictionary(x_train)
    #train_features = [dictionary.doc2bow(word) for word in x_train]
    #test_features = [dictionary.doc2bow(word) for word in x_test]
    ###### GENSIM ######
    
    ####### SKLEARN ###### 
    # Initialize the "CountVectorizer" object, which is scikit-learn's
    # bag of words tool.  
    vectorizer = CountVectorizer(analyzer = 'word', tokenizer = None, preprocessor = None, \
                                 stop_words = None, max_features = 5000, max_df=0.95) 

    # fit_transform() does two functions: First, it fits the model
    # and learns the vocabulary; second, it transforms our training data
    # into feature vectors. The input to fit_transform should be a list of 
    # strings.
    train_data_features = vectorizer.fit_transform(words_li)
    np.asarray(train_data_features)
    #print(train_data_features.shape)
    
    # for testing
    vocab = vectorizer.get_feature_names()
    print('Dataloading finishes\n')
    ###### SKLEARN ######

    # Training models
    print('Training starts')

    # unsupervised LDA
    topic_li = []
    train_log_perplex_li = []
    test_log_perplex_li = []

    no_top_words = 10
    no_topics = 10 # change the number based on different contributors, file length and etc.

    ###### SKLEARN ######
    #for i in range(1, no_topics + 1):
        #print('Topic number:', i)
        #topic_li.append(i)
        #for offset in [10]:
            #print('offset is:', offset)
    lda = LDA(n_topics=10, max_iter=20, learning_method='online', learning_decay=0.01, n_jobs=-1, random_state=1,
        learning_offset=15, doc_topic_prior=0.1, topic_word_prior=0.01).fit(train_data_features)
    display_topics(lda, vocab, no_top_words)
    '''
            #lda.transform(train_data_features)
            #perplexity = lda.perplexity(train_data_features)
            #print(np.log(perplexity))
            #print(perplexity)
            #perplex_li.append(perplexity)

    #train_log_perplex_li.append(np.log(perplex_li))
    ###### SKLEARN ######

    ###### GENSIM ######
    #for i in range(1, no_topics + 1):
    #model = gensim.models.ldamodel.LdaModel(train_features, num_topics=10, id2word = dictionary, passes=10)
    #for i in range(10):
    #    print(model.print_topic(i + 1))
        
        print('Topic number:', i)
        topic_li.append(i)
        perplex = model.bound(train_features)
        print("Perplexity: %s"%perplex)
        per_word_perplex = np.exp2(-perplex / sum(cnt for document in train_features for _, cnt in document))
        print("Per-word Perplexity: %s" % per_word_perplex)
        train_log_perplex_li.append(per_word_perplex)

        perplex = model.bound(test_features)
        print("Perplexity: %s"%perplex)
        per_word_perplex = np.exp2(-perplex / sum(cnt for document in test_features for _, cnt in document))
        print("Per-word Perplexity: %s" % per_word_perplex)
        test_log_perplex_li.append(per_word_perplex)
    '''
    ###### GENSIM ######
    print('Training ends')

    # plotting
    #plot(topic_li, train_log_perplex_li)
    #plot(topic_li, test_log_perplex_li)

if __name__=='__main__':
    main()