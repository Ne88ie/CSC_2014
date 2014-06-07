# coding=utf-8
from __future__ import print_function
import codecs

__author__ = 'annie'


def print_estimates(test_file, estimator_file):
    test_file = codecs.open(test_file, 'r', encoding="UTF8")
    estimator_file = codecs.open(estimator_file, 'r', encoding="UTF8")

    test = []

    for line in test_file:
        line = line.strip()
        if line == "" or line[0] == "#":
            continue
        c = line.split()[5]
        test.append(c)

    estimator = estimator_file.read().strip().split()

    test_file.close()
    estimator_file.close()

    matrix = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]

    title = [u'B-ORG', u'I-ORG', u'B-PER', u'I-PER', u'O']

    for i in xrange(len(test)):
        try:
            matrix[title.index(test[i])][title.index(estimator[i])] += 1
        except(TypeError):
            print(test[i], estimator[i])
            continue

    print('\t\t'.join([' '] + title))

    accuracy = 0

    for i in xrange(len(matrix)):
        print(title[i], end='\t\t')
        print('\t\t'.join([str(w) for w in matrix[i]]))
        accuracy += matrix[i][i]

    accuracy /= len(test) * 1.0

    def prf(tp, fp, fn):
        precision = tp * 1.0 / (tp + fp) if tp + fp else tp * 1.0
        recall = tp * 1.0 / (tp + fn) if tp + fn else tp * 1.0
        f_measure = 2 * precision * recall / (precision + recall) if precision + recall else 0
        return precision, recall, f_measure

    print()

    tp_fp_fn = []

    for i in xrange(len(title)):
        print('%s:' % title[i])
        tp = matrix[i][i]
        fp = sum([m[i] for m in matrix[:i] + matrix[i + 1:]])
        fn = sum(matrix[i][:i] + matrix[i][i + 1:])
        tp_fp_fn.append((tp, fp, fn))
        print('\tprecision = %f\n\trecall = %f\n\tf_measure = %f' % prf(tp, fp, fn))

    print(u'\nAccuracy on all tokens =', accuracy)

    print(u'\nThe accuracy, recall and F-measure on the boundaries registered entities:')

    def build_interval_dict(tags, ind):
            intervel_dict = {}
            i = 0
            while i < len(test):
                if tags[i] == title[ind]:
                    begin = i
                    i += 1
                    while tags[i] == title[ind + 1] and i < len(test):
                        i += 1
                    intervel_dict[begin] = i - 1
                else:
                    i += 1
            return intervel_dict

    def on_boder(test_dict, estimator_dict):
        relevant = reduce(lambda acc, item:
                          acc + 1 if item[0] in test_dict and test_dict[item[0]] == item[1]
                          else acc,
                          estimator_dict.items(), 0)
        precision = relevant * 1.0 / len(estimator_dict) if len(estimator_dict) > 0 else 0.0
        recall = relevant * 1.0 / len(test_dict) if len(test_dict) > 0 else 0.0
        f_measure = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
        print('\tprecision = %f\n\trecall = %f\n\tf_measure = %f' % (precision, recall, f_measure))

    print('ORG:')
    test_dict_org = build_interval_dict(test, 0)
    estimator_dict_org = build_interval_dict(estimator, 0)
    on_boder(test_dict_org, estimator_dict_org)

    print('\nPER:')
    test_dict_per = build_interval_dict(test, 2)
    estimator_dict_per = build_interval_dict(estimator, 2)
    on_boder(test_dict_per, estimator_dict_per)

    print('\nRegistered entities:')
    test_dict_org.update(test_dict_per)
    estimator_dict_org.update(estimator_dict_per)
    on_boder(test_dict_org, estimator_dict_org)

    print('\nMicro-accuracy, micro-recall and micro-F-measure:')
    def get_prf(ind):
        tp = tp_fp_fn[ind][0] + tp_fp_fn[ind+1][0]
        fp = tp_fp_fn[ind][1] + tp_fp_fn[ind+1][1]
        fn = tp_fp_fn[ind][2] + tp_fp_fn[ind+1][2]
        return prf(tp, fp, fn)

    print('ORG:')
    print('\tmicro-precision = %f\n\tmicro-recall = %f\n\tmicro-f_measure = %f' % get_prf(0))
    print('\nPER:')
    print('\tmicro-precision = %f\n\tmicro-recall = %f\n\tmicro-f_measure = %f' % get_prf(1))

    print('\n\n')


if __name__ == '__main__':
    print('Results for Step 1:')
    print_estimates("../data/ru_corpus.test_with_feats.txt", "../data/out_step1.txt")

    print('Results for Step 2:')
    print_estimates("../data/ru_corpus.test_with_feats.txt", "../data/out_step2.txt")

