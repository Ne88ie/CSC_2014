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
        if c == '\n':
            continue
        sentence_text.append(c)
        if c in ".?!":
            sentence = ET.SubElement(root, 'sentence')
            sentence.text = ''.join(sentence_text)
            sentence_text = []
    sentence = ET.SubElement(root, 'sentence')
    sentence.text = ''.join(sentence_text)
    tree = ET.ElementTree(root)
    f = open("output.xml", 'w')
    tree.write(f, encoding="UTF-8", pretty_print=True, xml_declaration=True)
    f.close()


if __name__ == __name__:
    tokenize(argv[1], argv[2])