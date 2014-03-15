from lxml.etree import iterparse
from sys import argv

PARSE_RES = ""
TESTING_SET = ""
# Sentence is a strict interval: [start_pos, end_pos]. This is transformed into a dict: { start_pos: end_pos }.
INTERVALS_TESTING_SET = {}
INTERVALS_PARSE_RES = {}

### Utils ###

def build_testing_set():
    global TESTING_SET
    global INTERVALS_TESTING_SET
    iparse = iterparse(TESTING_SET)
    pos = 0
    for event, elem in iparse:
        if elem.tag == "source":
            length = len(elem.text)
            INTERVALS_TESTING_SET[pos] = pos + length
            pos += length + 1 # Spaces between sentences and new lines don't matter.
    # print INTERVALS_TESTING_SET

def build_parse_res():
    global PARSE_RES
    global INTERVALS_PARSE_RES
    iparse = iterparse(PARSE_RES)
    pos = 0
    for event, elem in iparse:
        if elem.tag == "sentence":
            length = len(elem.text) if not elem.text is None else 0
            INTERVALS_PARSE_RES[pos] = pos + length
            pos += length + 1
    # print INTERVALS_PARSE_RES

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
    return relevant_retrieved() * 1.0 / retrieved

def recall():
    global INTERVALS_TESTING_SET
    relevant = len(INTERVALS_TESTING_SET)
    return relevant_retrieved() * 1.0 / relevant

def f_measure():
    prec = precision()
    rec = recall()
    return 2 * prec * rec / (prec + rec)

def accuracy():
    global INTERVALS_TESTING_SET
    global INTERVALS_PARSE_RES
    rel_retr = relevant_retrieved()
    return rel_retr * 1.0 / (len(INTERVALS_TESTING_SET) + len(INTERVALS_PARSE_RES) - rel_retr) 

def main():
    global PARSE_RES
    global TESTING_SET

    PARSE_RES = argv[1]
    TESTING_SET = argv[2]

    build_testing_set()
    build_parse_res()

    print "\nPrecision: %s\nRecall: %s\nF-measure: %s\nAccuracy: %s\n" % (precision(),
                                                                          recall(),
                                                                          f_measure(),
                                                                          accuracy())

if __name__ == "__main__":
    main()
