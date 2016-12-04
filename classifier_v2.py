from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.cross_validation import cross_val_score
from sklearn.ensemble import RandomForestClassifier
import pickle
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

def classifier_logistic(features, targets):
    '''

    :param features: bag of words representation of our users' tweets
    :param targets: labels of these users
    :return: score of the learning algorithm
    '''
    print('--------------- Logistic Regression ---------------')


    lr = LogisticRegression()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)

    lr.fit(train_set,train_features)
    prediction = lr.predict(test_set)
    score = lr.score(test_set, test_features)

    print(score)

    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    t = targets
    tt = t.reshape(targets.shape[0], )
    print(A)
    print('Success: %f out of %d points' % (((A[0, 0] + A[1, 1]) / s), s))

    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/lr.p", "wb") as f:
        pickle.dump(lr, f)

    return score, prediction, lr.coef_

def classifier_randomforest(features, targets):
    '''

    :param features: bag of words representation of our users' tweets
    :param targets: labels of these users
    :return: score of the learning algorithm
    '''
    print('--------------- RandomForest Classifier ---------------')
    lr = RandomForestClassifier()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)

    lr.fit(train_set,train_features)
    prediction = lr.predict(test_set)
    score = lr.score(test_set, test_features)

    print(score)

    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)

    print(A)
    print('Success: %f out of %d points' % (((A[0, 0] + A[1, 1]) / s), s))

    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/rf.p", "wb") as f:
        pickle.dump(lr, f)

    return score, prediction

def classifier_svm(features, targets):
    print('---------- SVM ------------')

    svm = SVC()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)

    svm.fit(train_set, train_features)
    prediction = svm.predict(test_set)

    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    print(A)
    print('Success: %f out of %d points' % (((A[0, 0] + A[1, 1]) / s), s))


    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/svm.p", "wb") as f:
        pickle.dump(svm, f)


    return prediction

def classifier_lda(features, targets):

    print('---------- LDA -------------')

    lda = LinearDiscriminantAnalysis(priors=[0.5, 0.5])
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)

    lda.fit(train_set, train_features)
    prediction = lda.predict(test_set)

    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    t = targets
    tt = t.reshape(targets.shape[0], )
    print(A)
    print('Success: %f out of %d points' % (((A[0,0] + A[1,1])/s),s))


    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/lda.p", "wb") as f:
        pickle.dump(lda, f)

    return prediction

def classifier_qda(features, targets):

    print('---------- QDA ------------')
    qda = QuadraticDiscriminantAnalysis(priors=[0.5, 0.5])
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)

    qda.fit(train_set, train_features)
    prediction = qda.predict(test_set)

    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    print(A)
    print('Success: %f out of %d points' % (((A[0,0] + A[1,1])/s),s))


    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/qda.p", "wb") as f:
        pickle.dump(qda, f)


    return prediction






if __name__ == '__main__':

    import time
    import numpy as np

    np.set_printoptions(suppress=True)

    start = time.time()

    import pickle

    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/bow.p", "rb") as f:
        bag_of_words = pickle.load(f)
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/user_indexes.p", "rb") as f:
        user_indexes = pickle.load(f)
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/user_ids.p", "rb") as f:
        user_ids = pickle.load(f)
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/words_indexes.p", "rb") as f:
        word_indexes = pickle.load(f)
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/words_ids.p", "rb") as f:
        words = pickle.load(f)
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/labels.p", "rb") as f:
        targets = pickle.load(f)

    start = time.time()
    score, prediction, coef = classifier_logistic(bag_of_words, targets)
    print('Logistic Regression in %f s' % (time.time() - start))
    start = time.time()
    prediction = classifier_lda(bag_of_words, targets)
    print('LDA in  %f s' % (time.time() - start))
    start = time.time()
    #prediction = classifier_qda(bag_of_words, targets)
    #print('QDA: %f' % (time.time() - start))
    start = time.time()
    prediction = classifier_svm(bag_of_words, targets)
    print('SVM in %f s' % (time.time() - start))
    start = time.time()
    prediction = classifier_randomforest(bag_of_words, targets)
    print('Random Forest in %f s' % (time.time() - start))