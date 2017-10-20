####### GENSIM LDA for 10-K Filings #######

# GENSIM: wrapped python version of MALLET

# This is used to clean 10-K filings.

# 1 GB of data ~ 45 seconds ~ a few hundred files
# Its REALLY time consuming, cause we need to
# go through all texts several times
# sentence by sentence, paragraph by paragraph
# item by item

# This file cleans 10K filing

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
import gensim
import random

READ_FAIL = 0
DATA_DIR = '/media/peng/New Volume/10-K'
FILE_COUNT = 0

common_words = set(['company', 'will', 'value', 'information', 'years', 'upon', 'company\'s', 
    'fiscal', 'rate', 'based', 'report', 'sales', 'management', 'services', 'form', 'costs', 'related', 
    'tax', 'ended', 'certain', 'market', 'credit', 'products', 'amount', 'period', 'net', 'including', 
    'opertions', 'securities', 'cash', 'time', 'statements', 'income', 'section', 'common', 'assets', 
    'shares', 'business', 'plan', 'year', 'date', 'interest', 'december', 'agreement', 'stock', 'may', 
    'financial', 'million', 'shall'])

def file_filter(id_li):
    global READ_FAIL
    for file_name in os.listdir(DATA_DIR):
        # exception handling
        # some files are not utf-8 encoding
        # its hard to pre-determine file encoding
        # so ignore them, and continue, shouldnt be a lot those files
        try:
            full_path = DATA_DIR + '/' + file_name

            # search for the start of header section
            fp = open(full_path)
            start = 0
            for i, line in enumerate(fp):
                if file_name in line:
                    start = i
                    break
            fp.close()

            flag = 1
            num_of_words = 0
            f = open(full_path)
            for i, line in enumerate(f):
                if 'filed as of date:' in line.lower():
                    # check if date if earlier than june 1 1996
                    date = int(line.split('\t')[-1][:-1])
                    if date < 19960601:
                        flag = 0
                if 'CONFORMED SUBMISSION TYPE' in line:
                    # check if Form 10-K405s
                    form = line.split('\t')[-1][:-1]
                    if form == '10-K405':
                        flag = 0
                # file length constraint
                num_of_words += len(line.split(' '))
            if num_of_words < 3000:
                flag = 0
            f.close()
            if flag:
                id_li.append(full_path)

            if len(id_li) % 1000 == 0:
                print(len(id_li), 'files visited')
        except:
            READ_FAIL += 1
            continue

    return id_li

def html_strip(string):
    # setting up for paragraphs splitting
    temp = string.replace('<p>', '\t')
    temp = temp.replace('</p>', '\n')
    # remove tags and some cleaning-up after tag removal
    temp = re.sub('&\w+', '', re.sub('<[^<]+?>', '', temp))
    temp = re.sub(';', '', temp)

    return temp

def item_split(data):
    # still in work
    return data

def line_metric_count(line):
    numbers = sum(c.isdigit() for c in line)
    words   = sum(c.isalpha() for c in line)
    spaces  = sum(c.isspace() for c in line)
    total = len(line)
    num_alphanumeric = numbers + words
    num_char = total - spaces

    return num_alphanumeric, num_char

def line_restriction(data):
    temp = []
    count = 0
    for line in data:
        count += 1
        num_alphanumeric, num_char = line_metric_count(line)
        # line length restriction
        if num_alphanumeric > 15 and num_char > 20:
            if '<' not in line and '>' not in line:
                temp.append(line)

    return temp

def para_restriction(data):
    # use tabs to identify paragraphs
    for i in range(len(data)):
        data[i] = data[i].replace('    ', '\t')

    flag = 0
    para_count = 0 
    temp = []
    para = []
    para_char = 0
    para_alphanumeric = 0
    for item in data:
        if '\t' in item:
            flag = 1 - flag
            para_count += 1
        if flag:
            if len(para) == 0:
                para.append('\n' + str(para_count) + '\n')
            para.append(item)

        elif len(para) > 0:
            # filtering and re-initialize
            for line in para:
                num_alphanumeric, num_char = line_metric_count(line)
                para_char += num_char
                para_alphanumeric += num_alphanumeric
            
            if para_char > 80 and para_alphanumeric / para_char >= 0.5:
                temp.append(para)
            
            para = []
            flag = 1
            para_char = 0
            para_alphanumeric = 0
            #para.append('\n' + str(para_count) + '\n')
            para.append(item)

    return temp
    
def file_clean(file):
    data = []
    f = open(file)
    flag_type = 0
    flag_text = 0
    for i, line in enumerate(f):
        if flag_text and flag_type:
            if '<S>' not in line and '<C>' not in line:
                new_line = html_strip(line)
                data.append(new_line)
                
        if '<TYPE>10-K' in line:
            flag_type = 1
        if flag_type and '<TEXT>' in line:
            flag_text = 1
        if flag_type and '</TEXT>' in line:
            flag_text = 0
            break

    #out_file = 'test/' + file.split('/')[-1]
    out_file = file.split('/')[-1]

    # item split and cleaning
    output = item_split(data)
    # line and paragraph restriction
    output = line_restriction(output)
    output = para_restriction(output) 

    if len(output) > 0:
        # 'test_small/' + 
        with open('/home/peng/Desktop/10K_processed' + out_file, 'w') as fout:
            for para in output:
                fout.writelines(para)

    else:
        global FILE_COUNT
        FILE_COUNT -= 1


def main():
    # how many data entries for our csv files, some double checking
    # prepare bag of words
    print('Dataloading Starts')
    words_li = []
    id_li = []

    # filings filtering
    file_filter(id_li)
    print('Number of files:', len(id_li))
    global FILE_COUNT
    FILE_COUNT = len(id_li)

    # file cleaning
    for item in id_li:
        file_clean(item)

    print('Dataloading Stops')
    print('Number of files after processing:', FILE_COUNT)
    
    global READ_FAIL
    print('Number of reading failure:', READ_FAIL)


if __name__=='__main__':
    main()