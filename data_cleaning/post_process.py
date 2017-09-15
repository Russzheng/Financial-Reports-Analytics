# Basically, pdfs (not scanned copies, those are images, hard to parse)
# consist of small sections that hold absolute position values and information (text or image or whatever)
# so we converted pdfs to xmls first. ANd all those small sections hold tag 'text'
# In this file, we extract information from those tags and strip useless information
# It is not a perfect method to clean data
# and it varies from one contributor to another

# Written in multiprocess manner
# convert 1k xmls to txts ~ 2 seconds

import xml.etree.ElementTree as ET
import os
import multiprocessing
import concurrent.futures
import csv

# list of failed conversions
FAIL_LI = []

# modify these directories if needed
DATA_DIR = '/home/peng/Desktop/data_cleaning/xml'
TEXT_DIR = '/home/peng/Desktop/data_cleaning/textfiles'
FAIL_DIR = '/home/peng/Desktop/data_cleaning/failure'
OUTPUT_DIR = '/home/peng/Desktop/data_cleaning/output'

# Check and create directories if needed
if not os.path.isdir(TEXT_DIR):
    os.makedirs(TEXT_DIR)

if not os.path.isdir(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Keywords for disclaimer and etc.
BAD_WORDS = ['disclaimer', 'disclosure']

# function to get the list of file names to convert from xml 2 txt
def get_file_list():
    file_li = os.listdir(DATA_DIR)
    if 'corrupt_log.txt' in file_li:
        file_li.remove('corrupt_log.txt')
    if 'filter.sh' in file_li:
        file_li.remove('filter.sh')
    return sorted(file_li)

# extract useful texts from xml files
def text_extraction(file_name):
    global FAIL_LI
    # parse the file
    try:
        file = ET.parse(DATA_DIR + '/' + file_name)
        root = file.getroot()
    except:
        if file_name not in FAIL_LI:
            FAIL_LI.append([file_name])
    # strip lines that contain 'fontspec tag'
    for parent in root.findall('.//fontspec/..'):
        for element in parent.findall('fontspec'):
            parent.remove(element)

    #og_text_str = ''
    new_text_str = ''

    # count page number
    # look for disclaimer, disclosure and all dat mtfks.
    global BAD_WORDS
    page_num = 0
    page_li = []

    for page in list(root):
        page_num += 1
        
    for parent in root.findall('.//item/..'):
        for element in parent.findall('item'):
            if any(s in element.text.lower() for s in BAD_WORDS):
                temp = int(element.attrib['page'])
                if temp not in page_li and temp is not 1:
                    page_li.append(temp)

    # strip lines that have length < 15. 
    # ==>> lines that dont have sentences or partial sentences
    count = 0
    for page in list(root):
        count += 1
        if count in page_li:
            continue
        for parent in page.findall('.//text/..'):
            #new_text_str += 'PAGE: ' + str(count) + '\n'
            #og_text_str += 'PAGE: ' + str(count) + '\n'
            for element in parent.findall('text'):
                if element is None or element.text is None:
                    parent.remove(element)
                else:
                    # storing original texts for comparisons
                    #og_text_str += element.text + '\n'
                    if len(element.text) < 15:
                        parent.remove(element)
                    else:
                        new_text_str += element.text + '\n'
            #new_text_str += '\n'
            #og_text_str += '\n'

    # write xml file
    #file.write('test.xml')

    # write txt file
    new_text_file = open(TEXT_DIR + '/' + str(file_name[:-4]) + '.txt', 'w')
    new_text_file.write(new_text_str)
    new_text_file.close()

    if len(new_text_str) == 0:
        if file_name not in FAIL_LI:
            FAIL_LI.append([file_name])

# multiprocess to speed up massive conversions
def multiprocess(file_name):
    try:
        text_extraction(file_name)
    except:
        # record failed conversions and move those xmls to failed folder
        # exception handling
        if file_name not in FAIL_LI:
            FAIL_LI.append([file_name])
        #os.rename(DATA_DIR + '/' + file_name, FAIL_DIR + '/' + file_name)
    #text_extraction(file_name)

# log the failed conversion
def record_fail():
    global FAIL_LI
    if len(FAIL_LI) == 0:
        FAIL_LI.append(['No failed conversions!'])
    else:
        FAIL_LI = sorted(FAIL_LI)

    with open(OUTPUT_DIR + '/' + 'failure_2txt.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(FAIL_LI)
    outFile.close()

def main():
    # get file list
    file_li = get_file_list()
    #file_li = ['15053640.xml', '15057054.xml']
    
    # text extraction
    # multiprocess for speeed
    
    executor = concurrent.futures.ProcessPoolExecutor(10)
    futures = [executor.submit(multiprocess, file_name) for file_name in file_li]
    concurrent.futures.wait(futures)
    
    # logging
    record_fail()

if __name__=='__main__':
    main()