import os
import csv
import multiprocessing
import concurrent.futures
from shutil import copyfile

CMD = 'pdftohtml -q -i -xml -c /home/peng/Desktop/dataset_selection/data/'
src = '/home/peng/Desktop/dataset_selection/data/'

# Destination directory where all successfully converted xml files are stored
dst = '/home/peng/Desktop/readability/data'
# Destination directory where all pdfs that failed conversions will be moved to this folder
fail_dst = '/home/peng/Desktop/readability/failure'

output_dst = '/home/peng/Desktop/readability//output'

# Check and create directories if needed
if not os.path.isdir(dst):
    os.makedirs(dst)
if not os.path.isdir(fail_dst):
    os.makedirs(fail_dst)
if not os.path.isdir(output_dst):
    os.makedirs(output_dst)

# multi-processing for speed
# since python program is CPU bounded
# multithreading wont work, we multi-process instead
def multitask_this_shit(item):
    command = CMD + str(item) + ' ' + dst + str(item)[:-4]
    dst_file = dst + str(item)[:-4] + '.xml'
    try:
        if not os.path.isfile(dst_file):
            os.system(command)
    except:
        if not os.path.isfile(dst_file):
            os.rename(src + str(item), fail_dst + str(item))

if __name__=='__main__':

    # Directory where all pdfs are stored
    file_li = []
    for dirpath, dirnames, filenames in os.walk(src):
        for filename in [f for f in filenames if f.endswith('.pdf')]:
            file_li.append(os.path.join(dirpath, filename))
    print(file_li[0])
    print(len(file_li))
    exit()

    if 'corrupt_log.txt' in file_li:
        file_li.remove('corrupt_log.txt')
    if 'filter.sh' in file_li:
        file_li.remove('filter.sh')

    executor = concurrent.futures.ProcessPoolExecutor(10)
    futures = [executor.submit(multitask_this_shit, item) for item in file_li]
    concurrent.futures.wait(futures)

    # Document conversion failure
    fail_li = []
    suc_li = []
    
    fail_file = os.listdir(fail_dst)
    if len(fail_file) > 0:
        for item in fail_file:
            fail_li.append([item])

    if len(fail_li) == 0:
        fail_li.append(['No failed conversions!'])
    else:
        fail_li = sorted(fail_li)

    success_file = os.listdir(src)
    if len(success_file) > 0:
        for item in success_file:
            suc_li.append([item])

    if len(suc_li) == 0:
        suc_li.append(['No successful conversions!'])
    else:
        suc_li = sorted(suc_li)

    with open(output_dst + '/' + 'failure_2xml.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(fail_li)
    outFile.close()
    
    with open(output_dst + '/' + 'success_2xml.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(suc_li)
    outFile.close()
