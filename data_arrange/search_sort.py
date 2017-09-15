# this is the file to find all pdf files/xml files in the hard disk
# and sort them
# some re-use of python functions in data_selection
import csv
import os
import shutil
import glob
import pandas as pd
import multiprocessing
import concurrent.futures
from shutil import copyfile

file_count = 0
err_li = []

pdf_succ_li = []
pdf_fail_li = []
pdf_err_li = []

xml_succ_li = []
xml_fail_li = []
xml_err_li = []

output_dst = '../output/'
# read two index files 
# output index.csv as final csv file
def read_init():
    fields = ['Report_num', 'Contributor', 'ticker']
    df = pd.read_csv('../index_files/sp500_index_files.csv', encoding='latin1', usecols=fields)
    df_smallcap = pd.read_csv('../index_files/spsmallcap_index_files.csv', encoding='latin1', usecols=fields)
    df_new = pd.concat([df, df_smallcap])
    
    # remove duplicates and non-numerics
    df_new['Report_num'] = df_new['Report_num'].apply(pd.to_numeric, errors='ignore', downcast='integer')
    df_new = df_new.drop_duplicates(subset=['Report_num'], keep='first')
    df_new = df_new.dropna(subset=['Report_num'], axis=0)
    df_new = df_new.sort_values('Report_num')
    df_new = df_new[fields]

    # remove "". I did it manually. Replace function in sublime.
    df_new.to_csv('../index_files/index_final.csv', encoding='utf-8', index=False, float_format="%.0f")


def count(path):
    # count number of xml/pdf files in the path
    pdf_count = 0
    xml_count = 0
    pdf_li = []
    xml_li = []
    for root, dirs, files in os.walk(path):
        for fname in files:
            if fname.lower().endswith('.xml'):
                xml_count += 1
                xml_li.append(int(fname[:-4]))
            if fname.lower().endswith('.pdf'):
                pdf_count += 1
                pdf_li.append(int(fname[:-4]))
            #print(os.path.join(root, fname))
            #print(fname)
    percentage = 200.0 * len(set(pdf_li) & set(xml_li)) / (len(pdf_li) + len(xml_li))
    print('Percentage:', percentage)
    print('pdf:', pdf_count) #pdf: 883548
    print('xml:', xml_count) #xml: 1142061

def find(name, path):
    # search the whole path
    # find the file
    # move it
    pdf_count = 0
    xml_count = 0
    for root, dirs, files in os.walk(path):
        for fname in files:
            if fname == str(name):
                return os.path.join(root, fname)
    
    return -1

def sort_file(rep_no, contri, ticker):
    global pdf_fail_li # list of non-existent files
    global pdf_succ_li # list of existent files
    global pdf_err_li # list of files that encounter errors

    global xml_fail_li # list of non-existent files
    global xml_succ_li # list of existent files
    global xml_err_li # list of files that encounter errors

    global file_count
    file_count += 1
    if file_count % 100 == 0:
        print('file number:', file_count)

    pdf_dirs = '/media/peng/New Volume' + '/Sorted_Analyst_Report/pdf/' + contri + '/' + ticker + '/' + str(rep_no) + '.pdf'
    xml_dirs = '/media/peng/New Volume' + '/Sorted_Analyst_Report/xml/' + contri + '/' + ticker + '/' + str(rep_no) + '.xml'
    pdf_name = str(rep_no) + '.pdf' 
    xml_name = str(rep_no) + '.xml'

    path = '/media/peng/New Volume'
    # First create directories
    # You probably wont need to uncomment the next few lines. I have already create all directories.
    #if not os.path.isdir(dirs):
    #    os.makedirs(dirs)
    '''if not os.path.isfile(pdf_dirs):
        #try:
        num = find(pdf_name, path)
        if num is not -1:
            print(num)
            pdf_succ_li.append([num])
            os.rename(num, pdf_dirs)
        else:
            pdf_fail_li.append([rep_no])
        except:
            pdf_err_li.append(rep_no)
    else:
        pdf_succ_li.append([pdf_dirs])
        '''
    
    if not os.path.isfile(xml_dirs):
        try:
            num = find(xml_name, path)
            if num is not -1:
                xml_succ_li.append([num])
                os.rename(num, xml_dirs)
            else:
                xml_fail_li.append([rep_no])
        except:
            xml_err_li.append(rep_no) 
    else:
        xml_succ_li.append([xml_dirs])

# multiprocess to speed up
def multiprocess(row):
    rep_no = row[0]
    contri = row[1]
    ticker = row[2]
    global err_li
    #global file_count
    #file_count += 1
    #try:
    sort_file(rep_no, contri, ticker)
    #except:
    #    err_li.append(rep_no)

def main():
    #count('/media/peng/My Passport')
    #read_init()
    count('/media/peng/New Volume')
    
    # sort pdfs and xmls 
    # multiprocess but probably wont speed up too much
    # as its IO bound
    with open('../index_files/index_final.csv', 'r') as f:
        reader = csv.reader(f)
        for idx, row in enumerate(reader):
            #if idx in range(1,10001):
            multiprocess(row)

    global pdf_fail_li # list of non-existent files
    global pdf_succ_li # list of existent files
    global pdf_err_li # list of files that encounter errors

    global xml_fail_li # list of non-existent files
    global xml_succ_li # list of existent files
    global xml_err_li # list of files that encounter errors

    global file_count

    print(len(pdf_succ_li))
    print(len(pdf_fail_li))
    print(len(pdf_err_li))

    print(len(xml_succ_li))
    print(len(xml_fail_li))
    print(len(xml_err_li))

    print(len(err_li))

    print(file_count)

    output_li = [pdf_succ_li, pdf_fail_li, pdf_err_li, xml_succ_li, xml_fail_li, xml_err_li]
    for li in output_li:
        if len(li) is 0:
            li = [['NO FILES']]

    with open(output_dst + 'pdf_success.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(pdf_succ_li)
    outFile.close()
    
    with open(output_dst + 'pdf_fail.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(pdf_fail_li)
    outFile.close()

    with open(output_dst + 'pdf_error.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(pdf_err_li)
    outFile.close()

    with open(output_dst + 'xml_success.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(xml_succ_li)
    outFile.close()
    
    with open(output_dst + 'xml_fail.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(xml_fail_li)
    outFile.close()

    with open(output_dst + 'xml_error.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(xml_err_li)
    outFile.close()
    

if __name__=='__main__':
    main()
