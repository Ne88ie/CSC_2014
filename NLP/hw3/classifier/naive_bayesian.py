# coding=utf-8
__author__ = 'annie'
from os import listdir
from os.path import join as path_join
from re import split as re_split, sub as re_sub, findall as re_findall
from pickle import dump, load
import random

with open(path_join('..', 'data', 'stopwords.txt')) as f:
    STOPWORDS = map(lambda w: w.rstrip(), f.readlines())


class NBClassifier(object):
    def __init__(self, kind_of_partition='word', ngram=4, stopwords=[]):
        self.trained_model = {}
        self.kind_of_partition = kind_of_partition
        self.ngram = ngram
        self.count_classes = [0.0, 0.0]
        self.stopwords = stopwords

    def get_features(self, source):
        """
        Feature extraction from text. The point where you can customize features.
        source - opened file
        return feature set, iterable object
        """
        words = []
        for line in source:
            if self.kind_of_partition == 'word':
                words.extend([word
                              for word in re_split('[\s,.:;!?<>+="()%\-0-9]', line.decode("utf-8").lower().encode("utf-8"))
                              if len(word) > 2 and
                              word not in self.stopwords])
                              # not is_bad(word.decode("utf-8"))])
            elif self.kind_of_partition == 'ngram':
                for word in re_split('[\s,.:;!?<>+="()%\-]', line.decode("utf-8").lower().encode("utf-8")):
                    if word and word not in self.stopwords:
                        words.extend(re_findall('.{1,%d}' % self.ngram, word))
        return words

    def init_trained_model(self, features, num_class):
        """
        Initializes the dictionary that stores counters features.
        features - feature set, iterable object
        num_class - class number whose value will be incremented, beginning with 0
        """
        for word in features:
            if word not in self.trained_model:
                self.trained_model[word] = [0.0, 0.0]
            self.trained_model[word][num_class] += 1

    def doc_prob(self, features, model):
        """
        Calculation of Pr (Document | of class) for both classes.
        """
        prob_0 = 1.0
        prob_1 = 1.0
        for feature in features:
            if feature not in model:
                continue
            prob_0 *= model[feature][0]
            prob_1 *= model[feature][1]
        return prob_0, prob_1

    def train(self, folder_class, folder_not_class, model_file):
        """
        Training model with class files and not class files.
        Expected that folder_class, folder_not_class, model_file in the folder "data".
        """
        # processing class files
        if type(folder_class) is list:
            list_file_class = folder_class
            folder_class = 'class'
        else:
            list_file_class = listdir(path_join('..', 'data', folder_class))
        for file_path in list_file_class:
            self.count_classes[0] += 1
            with open(path_join('..', 'data', folder_class, file_path)) as f:
                self.init_trained_model(self.get_features(f), 0)

        # processing files are not class
        if type(folder_not_class) is list:
            list_not_file_class = folder_not_class
            folder_not_class = 'no_class'
        else:
            list_not_file_class = listdir(path_join('..', 'data', folder_not_class))
        for file_path in list_not_file_class:
            self.count_classes[1] += 1
            with open(path_join('..', 'data', folder_not_class, file_path)) as f:
                self.init_trained_model(self.get_features(f), 1)

        # calculation of the weighted probabilities
        for key, val in self.trained_model.items():
            weight = 1
            assumedprob = 0.5
            if sum(val) < 4:
                del self.trained_model[key]
                continue
            val[0] = (weight * assumedprob + sum(val) * val[0] / self.count_classes[0]) / (sum(val) + 1)  # weighted probabilities
            val[1] = (weight * assumedprob + sum(val) * val[1] / self.count_classes[1]) / (sum(val) + 1)  # weighted probabilities

        # write this classifier in the file
        with open(path_join('..', 'data', model_file), 'wb') as f:
            dump(self, f)

    def count_conjugacy(self, true_marked_files, now_marked_files):
        """
        Return tru-positive, false-positive, false-negative.
        """
        tp = 0
        fp = 0
        fn = 0
        for key, val in true_marked_files.items():
            if val == 0 and now_marked_files[key] == 0:
                tp += 1
            if val == 0 and now_marked_files[key] == 1:
                fn += 1
            if val == 1 and now_marked_files[key] == 0:
                fp += 1
        return tp, fp, fn

    def test(self, folder_class, folder_not_class, model_file=None):
        """
        Classifies the input files, according to the trained model and returns precision, recall, f_measure.
        """
        # this branching for taking another trained classifier, according to a specified interface in the homework
        if model_file:
            with open(path_join('..', 'data', model_file), 'rb') as f:
                classifier = load(f)
                model = classifier.trained_model
                count_classes = classifier.count_classes
        else:
            model = self.trained_model
            count_classes = self.count_classes

        true_marked_files = {}
        now_marked_files = {}

        clprob_0 = count_classes[0] / sum(count_classes)
        clprob_1 = count_classes[1] / sum(count_classes)

        # processing class files
        if type(folder_class) is list:
            list_file_class = folder_class
            folder_class = 'class'
        else:
            list_file_class = listdir(path_join('..', 'data', folder_class))
        for file_path in list_file_class:
            true_marked_files['cl_' + file_path] = 0
            with open(path_join('..', 'data', folder_class, file_path)) as f:
                docprob_0, docprob_1 = self.doc_prob(self.get_features(f), model)
                now_marked_files['cl_' + file_path] = 0 if docprob_0 * clprob_0 > docprob_1 * clprob_1 else 1

        # processing files are not class
        if type(folder_not_class) is list:
            list_not_file_class = folder_not_class
            folder_not_class = 'no_class'
        else:
            list_not_file_class = listdir(path_join('..', 'data', folder_not_class))
        for file_path in list_not_file_class:
            true_marked_files['nocl_' + file_path] = 1
            with open(path_join('..', 'data', folder_not_class, file_path)) as f:
                docprob_0, docprob_1 = self.doc_prob(self.get_features(f), model)
                now_marked_files['nocl_' + file_path] = 0 if docprob_0 * clprob_0 > docprob_1 * clprob_1 else 1

        # calculate estimates
        tp, fp, fn = self.count_conjugacy(true_marked_files, now_marked_files)
        precision = tp * 1.0 / (tp + fp) if tp+fp else tp * 1.0
        recall = tp * 1.0 / (tp + fn) if tp+fn else tp * 1.0
        f_measure = 2 * precision * recall / (precision + recall) if precision+recall else 0
        return precision, recall, f_measure


def cross_validate():
    prec = 0.0
    rec = 0.0
    f_m = 0.0

    with open('cross-validation_results.txt', 'w') as res:
        for i in xrange(10):
            cl = NBClassifier(stopwords=STOPWORDS)
            files_class = ['01.txt', '02.txt', '03.txt', '04.txt', '05.txt', '06.txt', '07.txt', '08.txt', '09.txt', '10.txt',
                           '11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '20.txt',
                           '21.txt', '22.txt', '23.txt', '24.txt', '25.txt', '26.txt', '27.txt', '28.txt', '29.txt', '30.txt']
            files_noclass = ['01.txt', '02.txt', '03.txt', '04.txt', '05.txt', '06.txt', '07.txt', '08.txt', '09.txt', '10.txt',
                             '11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '20.txt',
                             '21.txt', '22.txt', '23.txt', '24.txt', '25.txt', '26.txt', '27.txt', '28.txt', '29.txt', '30.txt']

            random.shuffle(files_class)
            random.shuffle(files_noclass)

            files_train_class = sorted(files_class[:20])
            files_train_noclass = sorted(files_noclass[:20])

            files_test_class = sorted(files_class[20:])
            files_test_noclass = sorted(files_noclass[20:])

            cl.train(files_train_class, files_train_noclass, 'model.db')

            res.write("Iteration #%d\n" % (i + 1))
            res.write("Training set:\nClass: " + str(files_train_class) + "\nNo class: " + str(files_train_noclass))
            res.write("\nTesting set:\nClass: " + str(files_test_class) + "\nNo class: " + str(files_test_noclass))

            prec_cur, rec_cur, f_m_cur = cl.test(files_test_class, files_test_noclass)
            prec += prec_cur
            rec += rec_cur
            f_m += f_m_cur

            res.write("\nResults: precision %f, recall %f, F-measure %f\n\n" % (prec_cur, rec_cur, f_m_cur))

        prec /= 10.0
        rec /= 10.0
        f_m /= 10.0
        res.write("Average precision %f, average recall %f, average F-measure %f\n" % (prec, rec, f_m))

    with open('feats.txt', 'w') as f:
        for key, val in cl.trained_model.items():
            f.write('%s : %s \n' % (key, str(val)))


def old_main():
    # test with features-word
    cl1 = NBClassifier(stopwords=STOPWORDS)
    cl1.train(
        ['11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '20.txt',
         '21.txt', '22.txt', '23.txt', '24.txt', '25.txt', '26.txt', '27.txt', '28.txt', '29.txt', '30.txt'],
        ['11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '20.txt',
         '21.txt', '22.txt', '23.txt', '24.txt', '25.txt', '26.txt', '27.txt', '28.txt', '29.txt', '30.txt'],
              'model.db')
    print 'test 1:', cl1.test(['01.txt', '02.txt', '03.txt', '04.txt', '05.txt', '06.txt', '07.txt', '08.txt', '09.txt', '10.txt'],
              ['01.txt', '02.txt', '03.txt', '04.txt', '05.txt', '06.txt', '07.txt', '08.txt', '09.txt', '10.txt']
        )
    # (0.5277777777777778, 0.95, 0.6785714285714285) - 33%  on train
    # (0.6428571428571429, 0.9, 0.75) - 66% on train

    # test with features-4gram
    cl2 = NBClassifier('ngram', 4, stopwords=STOPWORDS)
    cl2.train(['01.txt', '02.txt', '03.txt', '04.txt', '05.txt', '06.txt', '07.txt', '08.txt', '09.txt', '10.txt'],
              ['01.txt', '02.txt', '03.txt', '04.txt', '05.txt', '06.txt', '07.txt', '08.txt', '09.txt', '10.txt'],
              'model.db')
    print 'test 2:', cl2.test(
        ['11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '20.txt',
         '21.txt', '22.txt', '23.txt', '24.txt', '25.txt', '26.txt', '27.txt', '28.txt', '29.txt', '30.txt'],
        ['11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '20.txt',
         '21.txt', '22.txt', '23.txt', '24.txt', '25.txt', '26.txt', '27.txt', '28.txt', '29.txt', '30.txt'])
    # (0.5, 1.0, 0.6666666666666666) - 33%  on train
    # (0.5, 1.0, 0.6666666666666666) - 66% on train

    # test with features-2gram
    cl3 = NBClassifier('ngram', 2, stopwords=STOPWORDS)
    cl3.train(['01.txt', '02.txt', '03.txt', '04.txt', '05.txt', '06.txt', '07.txt', '08.txt', '09.txt', '10.txt'],
              ['01.txt', '02.txt', '03.txt', '04.txt', '05.txt', '06.txt', '07.txt', '08.txt', '09.txt', '10.txt'],
              'model.db')
    print 'test 3:', cl3.test(
        ['11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '20.txt',
         '21.txt', '22.txt', '23.txt', '24.txt', '25.txt', '26.txt', '27.txt', '28.txt', '29.txt', '30.txt'],
        ['11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '20.txt',
         '21.txt', '22.txt', '23.txt', '24.txt', '25.txt', '26.txt', '27.txt', '28.txt', '29.txt', '30.txt'])
    # (0.6, 0.15, 0.24) - 33%  on train
    # (0.45454545454545453, 0.25, 0.3225806451612903)) - 66% on train


    with open('feats.txt', 'w') as f:
        for key, val in cl1.trained_model.items():
            f.write('%s : %s \n' % (key, str(val)))


if __name__ == "__main__":
    cross_validate()
