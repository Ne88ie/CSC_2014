__author__ = 'lia'
# -*- coding: utf-8 -*-
from lxml import etree as ET
from sys import argv
import codecs


def tokenize(input_file, output_file):
    input = codecs.open(input_file, 'r', encoding="UTF8")
    sentence_text = []
    root = ET.Element('sentences')
    while True:
        c = input.read(1)
        if "" == c:
            break
            #if c == '\n':
        #    continue
        sentence_text.append(c)
        next = None
        next_next = None
        if c in ".?!":
            flag = False
            next = input.read(1)
            if next == '':
                break
            if next != " " and next != '\n':
                sentence_text.append(next)
            else:
                next = input.read(1)
                if next.isupper():
                    flag = True
                elif next == '"':
                    next_next = input.read(1)
                    if next_next.isupper():
                        flag = True
                    else:
                        sentence_text.append(next)
                        sentence_text.append(next_next)
                        continue

            if flag:
                sentence = ET.SubElement(root, 'sentence')
                sentence.text = ''.join(sentence_text)
                sentence_text = []
                sentence_text.append(next)
                if (next_next != None):
                    sentence_text.append(next_next)
    sentence = ET.SubElement(root, 'sentence')
    sentence.text = ''.join(sentence_text)
    tree = ET.ElementTree(root)
    f = open(output_file, 'w')
    tree.write(f, encoding="UTF-8", pretty_print=True, xml_declaration=True)
    f.close()


if __name__ == __name__:
    tokenize(argv[1], argv[2])