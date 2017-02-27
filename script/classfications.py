import os, csv, time
import pickle
import numpy as np

from sklearn import svm, tree
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction import FeatureHasher
from collections import Counter
from pdb import set_trace

from random import randint, random, seed, shuffle



from ABCD import ABCD

base_dir = os.path.abspath(os.path.dirname(__file__))
sentence_vectors_csv = os.path.join(base_dir, 'sv.csv')

"split data according to target label"


def split_two(corpus, label, target_label):
    pos = []
    neg = []
    for i, lab in enumerate(label):
        if lab == target_label:
            pos.append(i)
        else:
            neg.append(i)
    positive = corpus[pos]
    negative = corpus[neg]
    # positive = [corpus[i] for i in pos]
    # negative = [corpus[i] for i in neg]
    return {'pos': positive, 'neg': negative}


"smote"


def smote(data, num, k=5):
    corpus = []
    nbrs = NearestNeighbors(n_neighbors=k + 1, algorithm='ball_tree').fit(data)
    distances, indices = nbrs.kneighbors(data)
    for i in range(0, num):
        mid = randint(0, len(data) - 1)
        nn = indices[mid, randint(1, k)]
        datamade = []
        for j in range(0, len(data[mid])):
            gap = random()
            datamade.append((data[nn, j] - data[mid, j]) * gap + data[mid, j])
        corpus.append(datamade)
    corpus = np.array(corpus)
    return corpus


"SVM"


def do_classification(train_data, test_data, train_label, test_label, clf='', learner='',ker=''):
    if not clf:
        # clf = svm.SVC(kernel=ker)
        clf = tree.DecisionTreeClassifier()
    clf.fit(train_data, train_label)
    prediction = clf.predict(test_data)
    abcd = ABCD(before=test_label, after=prediction)
    F2 = np.array([k.stats()[-1] for k in abcd()])
    F1 = np.array([k.stats()[-2] for k in abcd()])
    P = np.array([k.stats()[1] for k in abcd()])
    R = np.array([k.stats()[0] for k in abcd()])
    labeltwo = list(set(test_label))
    if 'pos' in labeltwo[0]:
        labelone = 0
    else:
        labelone = 1
    try:
        return P[labelone], R[labelone], F1[labelone], F2[labelone]
    except:
        pass


"cross validation"


def cross_val(clf='', data=[], label=[], target_label='', folds=5, learner='', kernel=[], title=''):
    "split for cross validation"

    def cross_split(corpus, folds, index):
        i_major = []
        i_minor = []
        l = len(corpus)
        for i in range(0, folds):
            if i == index:
                i_minor.extend(range(int(i * l / folds), int((i + 1) * l / folds)))
            else:
                i_major.extend(range(int(i * l / folds), int((i + 1) * l / folds)))
        return corpus[i_minor], corpus[i_major]

    "generate training set and testing set"

    def train_test(pos, neg, folds, index, issmote="smote", neighbors=5):
        pos_test, pos_train = cross_split(pos, folds=folds, index=index)
        neg_test, neg_train= cross_split(neg, folds=folds, index=index)
        if issmote == "smote":
            num = int((len(pos_train) + len(neg_train)) / 2)
            pos_train = smote(pos_train, num, k=neighbors)
            neg_train = neg_train[np.random.choice(len(neg_train), num, replace=False)]
        data_train = np.vstack((pos_train, neg_train))
        data_test = np.vstack((pos_test, neg_test))
        label_train = ['pos'] * len(pos_train) + ['neg'] * len(neg_train)
        label_test = ['pos'] * len(pos_test) + ['neg'] * len(neg_test)

        "Shuffle"
        tmp = range(0, len(label_train))
        shuffle(tmp)
        data_train = data_train[tmp]
        label_train = np.array(label_train)[tmp]

        tmp = range(0, len(label_test))
        shuffle(tmp)
        data_test = data_test[tmp]
        label_test = np.array(label_test)[tmp]

        return data_train, data_test, label_train, label_test

    # data, label = make_feature(corpus, method=feature, n_features=n_feature)
    data, label = np.array(data), np.array(label)
    split = split_two(corpus=data, label=label, target_label=target_label)
    pos = split['pos']
    neg = split['neg']

    print(str(len(pos)) + " positive-->" + str(target_label) + " in " + str(len(label)))

    start_time = time.time()
    measures = {'precision': [], 'recall': [], 'f1': [], 'f2': [] }
    # for i in range(folds):
    for i in range(10):
        tmp = range(0, len(pos))
        shuffle(tmp)
        pos = pos[tmp]
        tmp = range(0, len(neg))
        shuffle(tmp)
        neg = neg[tmp]
        for index in range(folds):
            data_train, data_test, label_train, label_test = \
                train_test(pos, neg, folds=folds, index=index, issmote='no')
            "SVM"
            p, r, f1, f2 = do_classification(data_train, data_test, label_train, label_test, clf=clf, ker='linear')
            measures['precision'].append(p)
            measures['recall'].append(r)
            measures['f1'].append(f1)
            measures['f2'].append(f2)
    res = measures
    print("\nTotal Runtime for [%s] in a %s-way cross val: --- %s seconds ---\n" % (title, str(folds), time.time() - start_time))
    return res


"get data & label from dict"
def get_data_label(input_dict={}, label_key=''):
    data, label = [], []
    for k, v in input_dict.iteritems():
        if k == label_key:
            label = v
        else:
            data.append[v]
    return data, label


def get_data_from_csv(input_csv):
    data, label = [], []
    jump_header = True
    with open(input_csv, 'r') as f:
        for doc in f.readlines():
            if jump_header:
                jump_header = False
                continue
            tmp = [float(i) for i in doc.split(',')]
            data.append(tmp[0:-1])
            label.append(int(tmp[-1]))
    return data, label



if __name__ == '__main__':
    learners = ['dual', 'primal']
    ker = ['linear', 'poly', 'rbf', 'sigmoid']
    vectors, labels = get_data_from_csv(sentence_vectors_csv)

    F_final = {}
    for learner in learners:
        F_final[learner] = cross_val(data=vectors, label=labels, target_label=labels[0], folds=5, learner=learner, kernel=ker)

    with open('dump/' + '_kernels.pickle', 'wb') as handle:
        pickle.dump(F_final, handle)
    print(F_final)
