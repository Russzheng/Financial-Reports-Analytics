# Double check IDs of the files we have collected

import os
import csv

li = []
with open('file_number/Initiation_report_number.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        li.append(int(row[0]))

success_li = []
for path, subdirs, files in os.walk('/home/peng/Desktop/dataset_selection/data'):
   for filename in files:
     f = os.path.join(path, filename)
     success_li.append(int(str(f)[42:-4]))
     
failure_li = set(li) - set(success_li)
failure_li = sorted(list(failure_li))
success_li = sorted(success_li)
temp_1 = []
temp_2 = []

for item in failure_li:
	temp_1.append([item])
for item in success_li:
	temp_2.append([item]) 

with open('/home/peng/Desktop/dataset_selection/output/doublecheck_failure.csv', 'w') as outFile:
    writer = csv.writer(outFile)
    writer.writerows(temp_1)
outFile.close()
with open('/home/peng/Desktop/dataset_selection/output/doublecheck_success.csv', 'w') as outFile:
    writer = csv.writer(outFile)
    writer.writerows(temp_2)
outFile.close()