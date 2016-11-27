from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split

def classifier(features, targets):
    '''

    :param features: bag of words representation of our users' tweets
    :param targets: labels of these users
    :return: score of the learning algorithm
    '''

    lr = LogisticRegression()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)

    lr.fit(train_set,train_features)
    prediction = lr.predict(test_set)
    score = lr.score(test_set, test_features)

    print(score)

    print(test_features)
    print(prediction)
    return score, prediction


def build_word_bag(dbname):
    from pymongo import MongoClient
    import time
    import numpy as np

    client = MongoClient()
    db = client[dbname]

    bag_of_words = db.words_occurences_by_user.find().limit(100000)

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

    M = np.array([[0 for i in words] for j in range(len(user_ids))])
    # Second passage : putting values into the empty matrix
    for doc in bag_of_words:
        user = doc['_id'][0]
        word = doc['_id'][1]
        count = doc['value']

        M[(user_ids[user], words[word])] = count

    for i in words:
        words_indexes[words[i]] = i
    for i in user_ids:
        user_indexes[user_ids[i]] = i

    return M, words_indexes, user_indexes


if __name__ == '__main__':

    from pymongo import MongoClient
    import time
    import numpy as np

    dbname = 'work_db'
    client = MongoClient()
    db = client[dbname]

    data = build_word_bag(dbname)
    bag_of_words = data[0]
    word_indexes = data[1]
    user_ids = data[2]

    print(bag_of_words.shape)
    n = bag_of_words.shape[0]
    targets = np.zeros((bag_of_words.shape[0]))
    print(user_ids)
    for j in user_ids:
        user_id = user_ids[j]
        label = db.users.find({"id": user_id})[0]['label']
        print(label)
        targets[j] = label

    print(targets)

    score, prediction = classifier(bag_of_words, targets)
