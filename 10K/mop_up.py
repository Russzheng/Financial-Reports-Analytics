import os

DATA_DIR = '/home/peng/Desktop/10K_processed'

count = 0

for file_name in os.listdir(DATA_DIR):
	full_path = DATA_DIR + '/' + file_name
	if os.stat(full_path).st_size == 0:
		count += 1
		os.remove(full_path)

print('# of empty files:', count)