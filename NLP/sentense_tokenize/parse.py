# IN_FILE = '../data/unmarked_corpora.txt'
IN_FILE = '../data/test.txt'

list_sentences = []

for line in open(IN_FILE, 'r'):
    prev_index = 0
    index = line.find('.')
    while index != -1:
        list_sentences.append(line[prev_index: index + 1])
        prev_index = index + 1
        index = line.find('.', index+1)
    current_sentence = line[prev_index: -1]

for i in list_sentences:
    print(i)