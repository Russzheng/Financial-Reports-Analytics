# Read corrupted files log and failure log.
# Compare with the initation list
# Get final dataset selection list
import csv
import os
import shutil
import glob

def read_failure():
    with open('file_number/fail.txt') as f:
        next(f)
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    content = [x[:-4] for x in content]
    return sorted(content)

def read_corrupted():
    li = []
    with open('file_number/corrupt_log.txt') as f:
        while True:
            line1 = f.readline()
            line2 = f.readline()
            if len(line1) > 1:
                temp = line1.split(' ')
                li.append(temp[0][:-4])
            if not line2: 
                break
    return sorted(li)

def read_init():
    li = []
    with open('file_number/Initiation_report_number.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            li.append(int(row[0]))
    return sorted(li)

# First try. Slow performance. But due to the nature of files searching and 
# copying. it wont be 'fast'. Also, the file size is huge. Will try to improve.
def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

def dataset_selection(li):
    fail_to_add = []
    add_li = []
    path = '/media/peng/My Passport'
    count = 0
    for item in li:
        count += 1
        temp = str(item) + '.pdf'
        filename = '/home/peng/Desktop/dataset_selection/data/' + temp
        search_path = find(temp, path)
        if count % 100 == 0:
            print('files visited', count)
        # check whether file exists
        if  os.path.isfile(filename):
            add_li.append([temp])
        else:
            if isinstance(search_path, str):
                shutil.copy2(search_path, '/home/peng/Desktop/dataset_selection/data')
            else:
                # find all files that system failed to find 
                fail_to_add.append([temp])
    # document all files that system failed to find
    with open('/home/peng/Desktop/dataset_selection/output/failure.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(fail_to_add)
    outFile.close()
    with open('/home/peng/Desktop/dataset_selection/output/success.csv', 'w') as outFile:
        writer = csv.writer(outFile)
        writer.writerows(add_li)
    outFile.close()
    print('Added %d files'%len(add_li))
    print('Failed to add %d files'%len(fail_to_add))
    print('Check failure.csv and success.csv for details.')

def main():
    # Checking before collecting dataset

    # get two list from the failure and corruption list
    fail_li = read_failure()
    corrupted_li = read_corrupted()
    # merge and deduplication 
    bad_li = fail_li + list(set(corrupted_li) - set(fail_li))
    
    # get initiation list
    good_li = read_init()

    temp = list(set(bad_li).intersection(good_li))
    corruption_rate = len(temp) / len(good_li)
    print('Corruption rate of the initiation files: {0:.2f}%'.format(corruption_rate*100))
    if len(temp) == 0:
        print('No bad files in initiation file list.')

    # move all initiation files to one folder
    good_li = list(set(good_li) - set(temp))
    dataset_selection(sorted(good_li))

if __name__=='__main__':
    main()