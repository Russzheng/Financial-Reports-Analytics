####### GENSIM LDA for 10-K Filings #######

# GENSIM: wrapped python version of MALLET

# This gensim library is incredibly slow. sklearn
# library's perplexity calculation method is all wrong
# and the paper used MALLET. So we stick with Gensim.

# But it is really slow

# This file applies the LDA model using Gensim

import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
import os, os.path
import numpy as np
from stemming.porter2 import stem
import matplotlib.pyplot as plt
from scipy.interpolate import spline
from gensim import corpora, models
from gensim.models import Phrases
import gensim
import random
import csv
import logging
import time

DATA_DIR = '/media/peng/New Volume/Back-up/Desktop/10K_processed'

common_words = set(['company', 'will', 'value', 'information', 'years', 'upon', 'company\'s', 
    'fiscal', 'rate', 'based', 'report', 'sales', 'management', 'services', 'form', 'costs', 'related', 
    'tax', 'ended', 'certain', 'market', 'credit', 'products', 'amount', 'period', 'net', 'including', 
    'opertions', 'securities', 'cash', 'time', 'statements', 'income', 'section', 'common', 'assets', 
    'shares', 'business', 'plan', 'year', 'date', 'interest', 'december', 'agreement', 'stock', 'may', 
    'financial', 'million', 'shall', 'style', 'block', 'display', 'color', 'border', 'bottom'])

def plot(topic_li, perplex_li, flag):
    topic_li = np.array(topic_li)
    perplex_li = np.array(perplex_li)

    topic_smooth = np.linspace(topic_li.min(), topic_li.max(), 400)
    per_smooth = spline(topic_li, perplex_li, topic_smooth)

    plt.plot(topic_smooth, per_smooth)
    plt.xlabel('number of topics', fontsize=16)
    plt.ylabel('log(perplexity)', fontsize=16)
    plt.show()

    if flag:
        plt.savefig('test_log_perplex_li.png')
    else:
        plt.savefig('train_log_perplex_li.png')

def train_test_split(x, test_pct):
    results = [], []
    for item in x:
        results[0 if random.random() < test_pct else 1].append(item)
    test, train = results
    np.asarray(test)
    np.asarray(train)
    return test, train

def load_data(file_name):
    # loading strings and manipulating strings are quite time consuming
    # A LOT file I/O 
    with open(file_name, 'r') as f:
        data = f.read().replace('\n', '')

    # lower case
    data = data.lower()
    # remove punctuations and numbers
    data = re.sub('[^a-zA-Z]', ' ', data)
    # split to words
    words = data.split()
    # delete stop words like 'the' 'a' and etc.
    # delete common words, 0.1% most frequent words
    stops = set(stopwords.words('english')) | common_words # use set for speed
    words = [w for w in words if w not in stops]

    return words

def main():
    start_time = time.time()
    # how many data entries for our csv files, some double checking
    # prepare bag of words
    print('Dataloading Starts') 
    # 10-40s for every 1K files loaded
    # when memoery is almost consumed, could take double the time
    words_li = []
    id_li = []
    for file_name in os.listdir(DATA_DIR):
        id_li.append(file_name)
        words_li.append(load_data(DATA_DIR + '/' + file_name))
        if len(id_li) >= 10000:
            break
        if len(id_li) % 1000 == 0:
            print(len(id_li), 'files processed')
            print('--- %s seconds ---' % (time.time() - start_time))

    data_size = len(id_li)
    print('Dataset size is :', data_size)

    # for some really bizzare cases
    #if len(words_li) != len(id_li):
    #    print('ERROR when loading data!')
    #    exit(9)
    
    np.asarray(words_li)

    ###### GENSIM  ######
    x_test, x_train = train_test_split(words_li, 0.1)

    # Create a dictionary representation of the documents.
    # Filter out words that occur less than 100 documents
    dictionary = corpora.Dictionary(x_train)
    dictionary.filter_extremes(no_below=100)

    train_features = [dictionary.doc2bow(word) for word in x_train]
    test_features = [dictionary.doc2bow(word) for word in x_test]
    
    # Training models
    print('Training starts')

    # unsupervised LDA
    topic_li = []
    train_log_perplex_li = []
    test_log_perplex_li = []

    no_top_words = 20
    #no_topics = 150 # change the number based on different contributors, file length and etc.

    for i in [10,50,100,150,200,250,300,400]:
        print('Topic number:', i)

        model = gensim.models.ldamodel.LdaModel(train_features, num_topics=i, id2word = dictionary, passes=8)

        if i == 10 or i == 150:
            data = model.print_topics(num_topics=-1, num_words=no_top_words)
            print(data)

            with open('topic_word_' + str(i) + '.csv','w') as out:
                csv_out = csv.writer(out)
                csv_out.writerow(['Topic_Number','Words'])
                for row in data:
                    csv_out.writerow(row)
            out.close()

        topic_li.append(i)
        perplex = model.bound(train_features)
        print('Perplexity: %s'%perplex)
        per_word_perplex = np.exp2(-perplex / sum(cnt for document in train_features for _, cnt in document))
        print('Per-word Perplexity: %s' % per_word_perplex)
        train_log_perplex_li.append(per_word_perplex)

        perplex = model.bound(test_features)
        print('Perplexity: %s'%perplex)
        per_word_perplex = np.exp2(-perplex / sum(cnt for document in test_features for _, cnt in document))
        print('Per-word Perplexity: %s' % per_word_perplex)
        test_log_perplex_li.append(per_word_perplex)
    
    print('Training ends')

    # plotting
    plot(topic_li, train_log_perplex_li, 0)
    plot(topic_li, test_log_perplex_li, 1)
    
    ###### GENSIM ######

if __name__=='__main__':
    main()