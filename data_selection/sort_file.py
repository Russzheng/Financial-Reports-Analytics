# This is the file to read the complete initation list
# and sort files into different folders based on company names

import pandas as pd
import numpy as np
import csv
import os
import os.path
import sys

DATA_DIRECTORY = '/home/peng/Desktop/dataset_selection/data/'

fields = ['Contributor', 'report_num']
df = pd.read_csv('file_number/full_initiation report id.csv', encoding='latin1', usecols=fields)

success_li = []
for dirpath, dirnames, filenames in os.walk('/home/peng/Desktop/dataset_selection/data'):
    for filename in [f for f in filenames if f.endswith(".pdf")]:
        success_li.append(int(filename[:-4]))

success_li = np.array(sorted(success_li))

def read_full_list():
    
    com_name_li = sorted(df['Contributor'].unique())
    com_name = pd.DataFrame(com_name_li, columns=['ContributorName'])
    com_name = com_name.reset_index(drop=True)
    com_name.to_csv('output/company_name.csv', index=True)
    
    com_freq_li = df['Contributor'].value_counts().reset_index()
    com_freq = pd.DataFrame(com_freq_li)
    com_freq.columns = ['Contributor', 'Frequency']
    com_freq = com_freq.sort_values('Contributor')
    com_freq = com_freq.reset_index(drop=True)
    com_freq.to_csv('output/company_frequency.csv', index=True)

    return com_freq

# Sort the data folder bt=y contributor name
def sort_files():
    gb = df.groupby('Contributor')
    gb = gb['report_num'].unique()
    gb = gb.reset_index() 

    for index, row in gb.iterrows():
        folder_name = row[0]
        id_li = row[1]
        id_li = sorted(row[1])

        folder_direct = DATA_DIRECTORY + folder_name

        if not os.path.exists(folder_direct):
            os.makedirs(folder_direct)

            for item in id_li:
                if item in success_li:
                    src = DATA_DIRECTORY + str(item) + '.pdf'
                    dst = folder_direct + '/' + str(item) + '.pdf'
                    os.rename(src, dst)
    

def main():
    #com_freq = read_full_list()
    sort_files()

if __name__=='__main__':
    main()