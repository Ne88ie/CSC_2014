__author__ = 'lia'

from collections import defaultdict
import math
from sys import argv
import codecs
from re import split as re_split

def get_word_vector(line):
    words = []
    for word in re_split('[\s,.:;!?<>d+="()%\-0-9]', line.lower()):
        if word != '' and word[0] != '@':
            words.append(word)
    return words


def add_new_words(d1, d2):
    for w in d2:
        d1[w] += 1


def get_words_for_class(file):
    f = codecs.open(file, 'r', encoding="UTF8")
    text = []
    n = 0
    # keys - words, values - number of documents containing this word
    words = defaultdict(int)
    for line in f:
        if line == "\n":
            n += 1
            add_new_words(words, text)
            text = []
        else:
            for w in get_word_vector(line):
                if w not in text:
                    text.append(w)
    f.close()
    return words, n


def get_chi_square_for_class(w, cl, non_cl, n1, n2):
    A = cl[w]
    B = non_cl[w]
    C = n1 - A
    D = n2 - B
    return 1.0 * (n1 + n2) * math.pow((A * D - C * B), 2) / ((A + C) * (B + D) * (A + B) * (C + D))


def get_chi_square(pos_file, neg_file):
    words_positive, n_pos = get_words_for_class(pos_file)
    words_negative, n_neg = get_words_for_class(neg_file)
    chi_square = defaultdict(lambda: (0.0, "neg"))
    for w in words_positive.keys():
        chi2_pos = get_chi_square_for_class(w, words_positive, words_negative, n_pos, n_neg)
        cl = "pos" if words_positive[w] > words_negative[w] else "neg"
        chi_square[w] = (chi2_pos, cl)
    for w in words_negative.keys():
        chi2_neg = get_chi_square_for_class(w, words_negative, words_positive, n_neg, n_pos)
        cl = "pos" if words_positive[w] > words_negative[w] else "neg"
        chi_square[w] = (chi2_neg, cl)
    return chi_square


def get_top_list(n, chi_res, c):
    chi_c = dict(filter(lambda (w, (chi, cl)): cl == c, chi_res.iteritems()))
    return map(lambda x: x[0], sorted(chi_c.iteritems(), key=(lambda el:el[1][0]), reverse=True)[:n])


def write_to_file_words(n, file1, file2):
    pos_file = argv[1]
    neg_file = argv[2]
    tmp = get_chi_square(pos_file, neg_file)
    f = codecs.open(file1, 'w', encoding="UTF8")
    for w in get_top_list(n, tmp, "pos"):
        f.write(w + "\n")
    f.close()
    f = codecs.open(file2, 'w', encoding="UTF8")
    for w in get_top_list(n, tmp, "neg"):
        f.write(w + "\n")
    f.close()

if __name__ == "__main__":
    write_to_file_words(200, "pos-words", "neg-words")