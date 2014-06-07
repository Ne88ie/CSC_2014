from lxml.etree import iterparse
from sys import argv

PARSE_RES = ""
TESTING_SET = ""
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
            dictname[pos] = pos + length
            pos += length + 1 # Spaces between sentences and new lines don't matter.
    # print dictname

###

def relevant_retrieved():
    global INTERVALS_TESTING_SET
    global INTERVALS_PARSE_RES
    return reduce(lambda acc, item:
                      acc + 1 if item[0] in INTERVALS_TESTING_SET and INTERVALS_TESTING_SET[item[0]] == item[1]
                              else acc,
                  INTERVALS_PARSE_RES.items(),
                  0)

def precision():
    global INTERVALS_PARSE_RES
    retrieved = len(INTERVALS_PARSE_RES)
    return relevant_retrieved() * 1.0 / retrieved if retrieved > 0 else 0.0

def recall():
    global INTERVALS_TESTING_SET
    relevant = len(INTERVALS_TESTING_SET)
    return relevant_retrieved() * 1.0 / relevant if relevant > 0 else 0.0

def f_measure():
    prec = precision()
    rec = recall()
    return 2 * prec * rec / (prec + rec) if prec + rec > 0 else 0.0

def accuracy():
    global INTERVALS_TESTING_SET
    global INTERVALS_PARSE_RES
    rel_retr = relevant_retrieved()
    fct = len(INTERVALS_TESTING_SET) + len(INTERVALS_PARSE_RES) - rel_retr
    return rel_retr * 1.0 / fct if fct > 0 else 0.0

def main():
    global PARSE_RES
    global TESTING_SET

    PARSE_RES = argv[1]
    TESTING_SET = argv[2]

    global PARSER_SENTENCE_TAG
    global TESTING_SET_SENTENCE_TAG

    if len(argv) >= 4:
        TESTING_SET_SENTENCE_TAG = argv[3]

    global INTERVALS_TESTING_SET
    global INTETVALS_PARSE_RES

    build_interval_set(TESTING_SET, INTERVALS_TESTING_SET, TESTING_SET_SENTENCE_TAG)
    build_interval_set(PARSE_RES, INTERVALS_PARSE_RES, PARSER_SENTENCE_TAG)

    print "\nPrecision: %s\nRecall: %s\nF-measure: %s\nAccuracy: %s\n" % (precision(),
                                                                          recall(),
                                                                          f_measure(),
                                                                          accuracy())

if __name__ == "__main__":
    main()
