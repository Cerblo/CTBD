from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.cross_validation import cross_val_score
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier

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
    t = targets
    tt = t.reshape(targets.shape[0], )
    print(A)
    print('Success: %f out of %d points' % (((A[0, 0] + A[1, 1]) / s), s))


    return score, prediction

def classifier_svm(features, targets):
    print('---------- SVM ------------')

    svm = SVC()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)

    svm.fit(train_set, train_features)
    prediction = svm.predict(test_set)

    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    t = targets
    tt = t.reshape(targets.shape[0], )
    print(A)
    print('Success: %f out of %d points' % (((A[0, 0] + A[1, 1]) / s), s))
    print('Score cross validation', cross_val_score(svm, features, tt))

    # print(np.transpose(np.vstack((np.transpose(test_set),np.transpose(prediction), np.transpose(test_features)))))

    return prediction

def classifier_lda(features, targets):

    print('---------- LDA -------------')

    lda = LinearDiscriminantAnalysis()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)

    lda.fit(train_set, train_features)
    prediction = lda.predict(test_set)

    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    t = targets
    tt = t.reshape(targets.shape[0], )
    print(A)
    print('Success: %f out of %d points' % (((A[0,0] + A[1,1])/s),s))
    # print(np.transpose(np.vstack((np.transpose(test_set),np.transpose(prediction), np.transpose(test_features)))))
    print('Score cross validation', cross_val_score(lda, features, tt,cv=10))

    return prediction

def classifier_qda(features, targets):

    print('---------- QDA ------------')
    qda = QuadraticDiscriminantAnalysis()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)

    qda.fit(train_set, train_features)
    prediction = qda.predict(test_set)

    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    print(A)
    print('Success: %f out of %d points' % (((A[0,0] + A[1,1])/s),s))
    f = features
    t = targets
    tt = t.reshape(targets.shape[0],)

    print('Score cross validation', cross_val_score(qda, f, tt))

    # print(np.transpose(np.vstack((np.transpose(test_set),np.transpose(prediction), np.transpose(test_features)))))

    return prediction


def getMinHash(dbname):
    db = client[dbname]

    hash = db.hashed_dataset.find()
    targets = np.empty((0,1))
    user_ids = np.empty((0,1))

    for doc in hash:
        try:
            id = int(doc['_id'])
            row = doc['x']
            label = doc['label']

            features = np.vstack((features, row))
            targets = np.vstack((targets, label))
            user_ids = np.vstack((user_ids, id))

        except NameError:
            features = np.array(row)
            targets = np.append(targets, label)
            user_ids = np.append(user_ids, id)

    return features, targets, user_ids


def build_word_bag(dbname):
    from pymongo import MongoClient
    import time
    import numpy as np

    client = MongoClient()
    db = client[dbname]

    bag_of_words = db.dataset_stop.find()

    words = {}
    words_indexes = {}
    user_ids = {}
    user_indexes = {}

    # First passage : fulfilling the list of words of the bag of words.
    for doc in bag_of_words:
        user = doc['_id']['user_id']
        word = doc['_id']['word']
        if user not in user_ids:
            user_ids[user] = len(user_ids)
        if word not in words:
            words[word] = len(words)

    M = np.zeros((len(user_ids), len(words)))

    bag_of_words = db.dataset_stop.find()
    # Second passage : putting values into the empty matrix
    for doc in bag_of_words:
        user = doc['_id']['user_id']
        word = doc['_id']['word']
        count = doc['value']

        M[(user_ids[user], words[word])] = count

    for i in words:
        words_indexes[words[i]] = i
    for i in user_ids:
        user_indexes[user_ids[i]] = i

    return M, words_indexes, user_indexes, user_ids


if __name__ == '__main__':

    from pymongo import MongoClient
    import time
    import numpy as np

    np.set_printoptions(suppress=True)

    dbname = 'work_db'
    client = MongoClient()
    db = client[dbname]

    data = build_word_bag(dbname)


    bag_of_words = data[0]
    word_indexes = data[1]
    user_ids = data[2]

    # Qualifying words importance by dividing by the sum
    for j in range(bag_of_words.shape[1]):
        for i in range(bag_of_words.shape[0]):
            value = bag_of_words[i,j]
            new_value = (value/np.sum(bag_of_words[i,:])) * np.log(bag_of_words.shape[0]/np.count_nonzero(bag_of_words[:,j]))
            bag_of_words[i,j] = new_value

    print(set([word_indexes[i] for i in np.argmax(bag_of_words,axis=1)]))
    print(len([word_indexes[i] for i in np.argmax(bag_of_words,axis=1)]))


    # Creation of target values
    targets = np.zeros((bag_of_words.shape[0]))

    for j in user_ids:
        user_id = user_ids[j]
        label = db.users.find({"_id": user_id})[0]['label']
        targets[j] = label




    # print(set([word_indexes[i] for i in np.argsort(bag_of_words)[15]]))
    # a = np.argsort(coef)
    # print(coef)
    # print(a)
    # print(set([word_indexes[i] for i in np.argsort(coef)[0,-10:]]))
    # print(set([word_indexes[i] for i in np.argsort(coef)[0,:10]]))


    score, prediction, coef = classifier_logistic(bag_of_words, targets)
    prediction = classifier_lda(bag_of_words, targets)
    prediction = classifier_qda(bag_of_words, targets)
    prediction = classifier_svm(bag_of_words, targets)

    prediction = classifier_randomforest(bag_of_words, targets)