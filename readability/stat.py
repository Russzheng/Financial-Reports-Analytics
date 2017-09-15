#1000 files / 20s
#input: python3 [python script] 
#need .csv dictionary and .xml in the same directory
#modify directories as needed
import os.path
from os import listdir
from sys import argv
import re
from readcalc import readcalc
import glob, os

class Processor(object):
    def __init__(self,input_file,dict_file):
        self.input_file=input_file

        # THE DIRECTORY TO STORE DATA/FILES AND DICTIONARY
        self.work_dir='/home/peng/Desktop/readability/data'
        
        self.dict_file=dict_file
        #self.dict_file='LoughranMcDonald_MasterDictionary_2014.csv'#to modify
        self.dict_dict={}#dict got from the dict_file
        self.dict_col=[] #record the first line -- the head of columns
        self.dict_result=[] # record a list of count numbers
        self.output_first_line=''
        self.update_dict(self.dict_file)

    def update_input_file(self,input_file):#update self.input_file
        self.input_file=input_file

    def process(self):
        self.dict_result=[0]*30
        raw_txt=''
        try:
            with open(self.input_file,'r',errors='ignore') as f:
                raw_txt=f.read()
        except:
            print('fail to read input file: '+self.input_file)
        processed_list, output=self.pre_process(raw_txt)
        for i in processed_list:
            if i.upper() in self.dict_dict:
                tmp=self.dict_dict[i.upper()]
                for j in range(6,15):#6-14, namely, begining with 'Negative' col
                    if int(tmp[j])>0:
                        self.dict_result[j]+=1
        for i in range(15,26):
            self.dict_result[i]=output[i-15]
        result=self.input_file.split('/')[-1][:-4]
        for i in range(6,26):
            result+=(','+str(self.dict_result[i]))
        result+='\n'

        return result


    def change_work_dir(self,new_dir):
        self.work_dir=new_dir
        #output_first_line
    def update_dict(self,dict_file): #update all dict related info
        #read the dictionary file
        dict_dict={}
        dict_col=[]
        dict_result=[]
        try:
            with open(self.dict_file,'r')as f:
                dict_col=f.readline().strip().split(',')
                dict_col.pop(0)
                dict_result=[0]*len(dict_col)
                for line in f:
                    tmp_list=line.strip().split(',')
                    word=tmp_list.pop(0)
                    dict_dict[word]=tmp_list
            self.dict_file=dict_file
            self.dict_dict=dict_dict
            self.dict_col=dict_col
            self.dict_result=dict_result
            tmp_head='File ID'
            for i in range(6,15):
                tmp_head+=(','+ str(dict_col[i]))
            tmp_head+=(','+'WordCount')
            tmp_head+=(','+'SentenceCount')
            tmp_head+=(','+'polysyllable_words')
            tmp_head+=(','+'flesch_reading_ease')
            tmp_head+=(','+'flesch_kincaid_grade_level')
            tmp_head+=(','+'coleman_liau_index')
            tmp_head+=(','+'gunning_fog_index')
            tmp_head+=(','+'smog_index')
            tmp_head+=(','+'ari_index')
            tmp_head+=(','+'lix_index')
            tmp_head+=(','+'dale_chall_score')
            tmp_head+='\n'
            self.output_first_line=tmp_head
        except:
            print('fail to update dict')

    def pre_process(self,s):

        result=s.split('<outline>')[0] #remove the ending outlines of xml
        result=re.sub('<[^>]*>',' ',result) #remove tags

        calc=readcalc.ReadCalc(result)
        output=[]
        metrics=calc.get_all_metrics()
        output.append(metrics[1])
        output.append(metrics[3])
        output.append(metrics[5])
        for i in range(8):
            output.append(metrics[-8+i])

        result=re.split('[^a-zA-Z]+',result) #split using all non-alphas
        result=list(filter(lambda x: x.isalpha(),result)) #remove useless words

        return result, output


def main():
    # Dictionary's directory
    file_list=[]
    for root, dirs, files in os.walk('/media/peng/New Volume'):
        for file in files:
            if file.endswith('.xml'):
                file_list.append(os.path.join(root, file))
    file_list.sort()
    print(len(file_list), 'xml files')

    processor=Processor('','/home/peng/Desktop/readability/LoughranMcDonald_MasterDictionary_2014.csv')
    file_count=0
    with open('output_2.csv','w')as f:
        f.write(processor.output_first_line)
        for i in file_list[761165:]:
            file_count+=1
            temp=str(i)
            processor.update_input_file(temp)
            f.write(processor.process())
            if file_count%10000 == 0:
                print(file_count, 'files visited.')
    print('HOORAY')
    #except:
    #    print('some error occurs, we have been processing in file name order\n, and now it is '+processor.input_file)

if __name__=='__main__':
    main()