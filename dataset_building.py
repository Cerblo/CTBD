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
    i=0
    for doc in bag_of_words:
        user = doc['_id']['user_id']
        word = doc['_id']['word']
        if user not in user_ids:
            user_ids[user] = len(user_ids)
        if word not in words:
            words[word] = len(words)
        i += 1
        if i%1000000 == 0:
            print(i)

    M = np.zeros((len(user_ids), len(words)))

    print("Passage 1 done")
    print('\n\n\n--------------------------\n\n\n' )

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

    return M, words_indexes, user_indexes, user_ids, words


if __name__ == '__main__':

    from pymongo import MongoClient
    import time
    import numpy as np

    np.set_printoptions(suppress=True)

    dbname = 'tweepoll_sample'
    client = MongoClient()
    db = client[dbname]
    start = time.time()
    print("Start process")
    data = build_word_bag(dbname)

    print('\n\n\n--------------------------\n\n\n' )
    print('Bag of words built in %f' % (time.time() - start))
    start = time.time()

    bag_of_words = data[0]
    word_indexes = data[1]
    user_indexes = data[2]
    user_ids = data[3]
    words = data[4]

    #Computing the sum of words for each user
    nb_words_by_user = [sum(bag_of_words[i,:]) for i in range(bag_of_words.shape[0])]
    print('nb_words_by_user OK in %f' % (time.time() - start))
    start = time.time()

    #Computing the number of documents that contain each word
    nb_users_by_word = [np.count_nonzero(bag_of_words[:,j]) for j in range(bag_of_words.shape[1])]
    print('nb_users_by_word OK in %f' % (time.time() - start))
    start = time.time()

    # Qualifying words importance by dividing by the sum
    for j in range(bag_of_words.shape[1]):
        for i in range(bag_of_words.shape[0]):
            value = bag_of_words[i,j]
            new_value = value/nb_words_by_user[i] * np.log(bag_of_words.shape[0]/nb_users_by_word[j])
            bag_of_words[i,j] = new_value
    print('tf - idf OK in %f' % (time.time() - start))
    start = time.time()

    import pickle

    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/bow_sample.p", "wb") as f:
        pickle.dump(bag_of_words, f)
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/user_indexes_sample.p", "wb") as f:
        pickle.dump(user_indexes, f)
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/user_ids_sample.p", "wb") as f:
        pickle.dump(user_ids, f)
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/words_indexes_sample.p", "wb") as f:
        pickle.dump(word_indexes, f)
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/words_ids_sample.p", "wb") as f:
        pickle.dump(words, f)


    # Creation of target values
    targets = np.zeros((bag_of_words.shape[0]))

    for id, index in user_ids:
        try:
            label = db.users.find({"_id": id})[0]['label']
            targets[index] = label
        except:
            print(id)

    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/labels_sample.p", "wb") as f:
        pickle.dump(targets, f)

    print('Serialization')
    print(bag_of_words.shape[0])




    print('Word bag: %f' % (time.time()- start))
