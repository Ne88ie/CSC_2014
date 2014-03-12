# coding=utf-8
from lxml.etree import iterparse


IN_FILE = '../data/annot.opcorpora.xml'
OUT_FILE = '../data/unmarked_corpora.txt'

def extract_text(iparse, out_file):
    with open(out_file, "w", ) as out:
        for event, elem in iparse:
            if elem.tag == 'paragraph':
                out.write(u'\n')
            elif elem.tag == 'source':
                out.write((elem.text + u' ').encode('utf-8'))


# check whether your code in the tag 'source' '\n'
def check_new_line(iparse):
    for event, elem in iparse:
        if elem.tag == 'source' and elem.text.find('\n') != -1:
            print('there is a new line')


if __name__ == '__main__':
    parse = iterparse(IN_FILE)
    check_new_line(parse)