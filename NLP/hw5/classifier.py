# coding=utf-8
from StringIO import StringIO
import codecs
from sys import argv

__author__ = 'annie'
from os import listdir
from os.path import join as path_join
from re import split as re_split, findall as re_findall
from pickle import dump, load

#with open(path_join('..', 'data', '-stopwords.txt')) as f:
#    STOPWORDS = map(lambda w: w.rstrip(), f.readlines())


class NBClassifier(object):
    def __init__(self, kind_of_partition='word', ngram=4, stopwords=[], est_words=[]):
        self.trained_model = {}
        self.kind_of_partition = kind_of_partition
        self.ngram = ngram
        self.count_classes = [0.0, 0.0]
        self.est_words = est_words
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
                              for word in re_split('[\s,.:;!?<>+="()%\-0-9d]', line.decode("utf-8").lower().encode("utf-8"))
                              if word and (not self.est_words or word in self.est_words)
                              and word not in self.stopwords])
                              # not is_bad(word.decode("utf-8"))])
            elif self.kind_of_partition == 'ngram':
                for word in re_split('[\s,.:;!?<>+="()%\-]', line.decode("utf-8").lower().encode("utf-8")):
                    if word and word not in self.stopwords and word not in self.stopwords:
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

    def extract_tweets(self, f):
        tweets = []
        current_tweet = ""
        for line in f:
            if line.strip() == "":
                tweets.append(StringIO(current_tweet))
                current_tweet = ""
                continue
            current_tweet += line
        return tweets

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
            list_file_class = listdir(folder_class)
        for file_path in list_file_class:
            self.count_classes[0] += 1
            with open(path_join(folder_class, file_path)) as f:
                for tweet in self.extract_tweets(f):
                    self.init_trained_model(self.get_features(tweet), 0)
                    tweet.close()

        # processing files are not class
        if type(folder_not_class) is list:
            list_not_file_class = folder_not_class
            folder_not_class = 'no_class'
        else:
            list_not_file_class = listdir(path_join(folder_not_class))
        for file_path in list_not_file_class:
            self.count_classes[1] += 1
            with open(path_join(folder_not_class, file_path)) as f:
                for tweet in self.extract_tweets(f):
                    self.init_trained_model(self.get_features(tweet), 1)
                    tweet.close()

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
        with open(path_join(model_file), 'wb') as f:
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
            with open(path_join(model_file), 'rb') as f:
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
            list_file_class = listdir(path_join(folder_class))
        for file_path in list_file_class:
            with open(path_join(folder_class, file_path)) as f:
                for i, tweet in enumerate(self.extract_tweets(f)):
                    true_marked_files['cl_' + str(i)] = 0
                    docprob_0, docprob_1 = self.doc_prob(self.get_features(tweet), model)
                    now_marked_files['cl_' + str(i)] = 0 if docprob_0 * clprob_0 > docprob_1 * clprob_1 else 1
                    tweet.close()

        # processing files are not class
        if type(folder_not_class) is list:
            list_not_file_class = folder_not_class
            folder_not_class = 'no_class'
        else:
            list_not_file_class = listdir(path_join(folder_not_class))
        for file_path in list_not_file_class:
            with open(path_join(folder_not_class, file_path)) as f:
                for i, tweet in enumerate(self.extract_tweets(f)):
                    true_marked_files['nocl_' + str(i)] = 1
                    docprob_0, docprob_1 = self.doc_prob(self.get_features(tweet), model)
                    now_marked_files['nocl_' + str(i)] = 0 if docprob_0 * clprob_0 > docprob_1 * clprob_1 else 1
                    tweet.close()

        # calculate estimates
        tp, fp, fn = self.count_conjugacy(true_marked_files, now_marked_files)
        precision = tp * 1.0 / (tp + fp) if tp+fp else tp * 1.0
        recall = tp * 1.0 / (tp + fn) if tp+fn else tp * 1.0
        f_measure = 2 * precision * recall / (precision + recall) if precision+recall else 0
        return precision, recall, f_measure


if __name__ == "__main__":
    est_words = []
    if len(argv) > 5 and argv[5] == "--est_words":
        for f in argv[6:]:
            with open(f, 'r') as fd:
                for line in fd:
                    line = line.strip()
                    if line:
                        est_words.append(line)

    classifier = NBClassifier('word', est_words=est_words)
    if argv[1] == "--train":
        classifier.train(argv[2], argv[3], argv[4])
    else:
        presition, recall, f_measure = classifier.test(argv[2], argv[3], argv[4])
        print "presition: %f, recall: %f, f_measure: %f" % (presition, recall, f_measure)