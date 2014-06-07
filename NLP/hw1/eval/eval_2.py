__author__ = 'annie'

from lxml.etree import iterparse
from sys import argv

# We use only XML format.
PARSER_SENTENCE_TAG = "sentence"
TESTING_SET_SENTENCE_TAG = "source"
# Sentence is a strict interval: [start_pos, end_pos]. This is transformed into a dict: { start_pos: end_pos }.
INTERVALS_TESTING_SET = {}
INTERVALS_PARSE_RES = {}
### Utils ###

def build_interval_set(filename, dictname, sentence_text_tag):
    iparse = iterparse(filename)
    pos = 0
    for event, elem in iparse:
        if elem.tag == sentence_text_tag:
            length = len(elem.text) if not elem.text is None else 0
            if length:
                for i in elem.text:
                    if not i.isalnum():
                        length -= 1
            dictname[pos] = pos + length
            pos += length  # Spaces between sentences and new lines don't matter.
    # print dictname, '\n'

###

def relevant_retrieved():
    global INTERVALS_TESTING_SET
    global INTERVALS_PARSE_RES
    return reduce(lambda acc, item:
                      acc + 1 if item[0] in INTERVALS_TESTING_SET and INTERVALS_TESTING_SET[item[0]] == item[1]
                      else acc,
                  INTERVALS_PARSE_RES.items(),
                  0)

def precision(relevant_retriev):
    global INTERVALS_PARSE_RES
    retrieved = len(INTERVALS_PARSE_RES)
    return relevant_retriev * 1.0 / retrieved if retrieved > 0 else 0.0

def recall(relevant_retriev):
    global INTERVALS_TESTING_SET
    relevant = len(INTERVALS_TESTING_SET)
    return relevant_retriev * 1.0 / relevant if relevant > 0 else 0.0

def f_measure(prec, rec):
    return 2 * prec * rec / (prec + rec) if prec + rec > 0 else 0.0

def accuracy(relevant_retriev):
    global INTERVALS_TESTING_SET
    global INTERVALS_PARSE_RES
    fct = len(INTERVALS_TESTING_SET) + len(INTERVALS_PARSE_RES) - relevant_retriev
    return relevant_retriev * 1.0 / fct if fct > 0 else 0.0

def main():
    PARSE_RES = argv[1]
    TESTING_SET = argv[2]
    OUT_FILE = argv[3]

    global PARSER_SENTENCE_TAG
    global TESTING_SET_SENTENCE_TAG

    global INTERVALS_TESTING_SET
    global INTETVALS_PARSE_RES

    build_interval_set(TESTING_SET, INTERVALS_TESTING_SET, TESTING_SET_SENTENCE_TAG)
    build_interval_set(PARSE_RES, INTERVALS_PARSE_RES, PARSER_SENTENCE_TAG)

    relevant_retriev = relevant_retrieved()
    p = precision(relevant_retriev)
    r = recall(relevant_retriev)
    text = "\nPrecision: %s\nRecall: %s\nF-measure: %s\nAccuracy: %s\n" % (p, r, f_measure(p, r), accuracy(relevant_retriev))
    with open(OUT_FILE, "w", ) as out:
        out.write(text.encode('utf-8'))

if __name__ == "__main__":
    main()

