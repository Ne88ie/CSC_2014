__author__ = 'lia'
# -*- coding: utf-8 -*-

import re
from sys import argv


def tokenize(input_file, output_file):
    output = open(output_file, 'w')
    output.write("<sentence>")
    for line in open(input_file, 'r'):
        regex = re.compile("[.?!]")
        out = regex.sub(line, "</sentence><sentence>")
        output.write(line)
    output.write("</sentence>")
    output.close()


if '__main__' == __name__:
    tokenize(argv[1], argv[2])