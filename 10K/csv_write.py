import csv

r = csv.reader(open('topic_word_150.csv')) 
lines = [l for l in r]

for i in range(1, len(lines)):
	temp = ''
	for j in range(1,40,2):
		temp += str(lines[i][1].split('"')[j]) + ' '
	lines[i][1] = temp


writer = csv.writer(open('topic_word_150_v2.csv', 'w'))
writer.writerows(lines)

r = csv.reader(open('topic_word_10.csv')) 
lines = [l for l in r]

for i in range(1, len(lines)):
	temp = ''
	for j in range(1,40,2):
		temp += str(lines[i][1].split('"')[j]) + ' '
	lines[i][1] = temp


writer = csv.writer(open('topic_word_10_v2.csv', 'w'))
writer.writerows(lines)