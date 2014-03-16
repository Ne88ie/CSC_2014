__author__ = 'lia'
# -*- coding: utf-8 -*-
from lxml import etree as ET
from sys import argv
import codecs


def tokenize(input_file, output_file):
    input = codecs.open(input_file, 'r', encoding="UTF8")
    sentence_text = []
    root = ET.Element('sentences')
    lookup = None
    while True:
        if not lookup:
            c = input.read(1)
        else:
            c = lookup
            lookup = None
        if "" == c:
            break
        if c == '\n':
            continue
        if c == '"' or c == u'«':
            sentence_text.append(c)
            next = input.read(1)
            while next != '"' and next != u'»':
                sentence_text.append(next)
                next = input.read(1)
            sentence_text.append(next)
            continue
        sentence_text.append(c)
        if c in ".!?":
            next = None
            if c == '.':
                next = input.read(1)
                if next != ' ' and next != '\n':
                    sentence_text.append(next)
                    continue
                else:
                    next_next = []
                    while next == ' ' or next == '\n':
                        next_next.append(next)
                        next = input.read(1)
                    if not next.isupper():
                        sentence_text.extend(next_next)
                        sentence_text.append(next)
                        continue
            sentence = ET.SubElement(root, 'sentence')
            sentence.text = ''.join(sentence_text).strip()
            sentence_text = []
            if next:
                lookup = next
    sentence = ET.SubElement(root, 'sentence')
    sentence.text = ''.join(sentence_text).strip()
    tree = ET.ElementTree(root)
    f = open(output_file, 'w')
    tree.write(f, encoding="UTF-8", pretty_print=True, xml_declaration=True)
    f.close()


if __name__ == __name__:
    tokenize(argv[1], argv[2])