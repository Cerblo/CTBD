from pymongo import MongoClient
import time
import numpy as np



def build_word_bag(dbname):

    '''

    :param dbname: name of the database we will extract data from
    :return: This function extracts the bag of words held in MongoDB into a Python object.
    It returns the bag of words, aside with user ids and work ids (that's to say the lines and columns values), in
    order to use it in our machine learning phase

    '''

    client = MongoClient()
    db = client[dbname]

    # Extracting the bag of words from Mongo as a simple cursor
    bag_of_words = db.dataset_stop.find()

    # Data structure that will store our data
    words = {}
    words_indexes = {}
    user_ids = {}
    user_indexes = {}

    # First loop : fulfilling the list of words of the bag of words.

    for doc in bag_of_words:
        user = doc['_id']['user_id']
        word = doc['_id']['word']
        if user not in user_ids:
            user_ids[user] = len(user_ids)
        if word not in words:
            words[word] = len(words)

    # As we have now the exact length of the matrix, we will fill out the matrix with occurrences
    M = np.zeros((len(user_ids), len(words))) # Initialization with zeros everywhere

    bag_of_words = db.dataset_stop.find() # We have to extract the cursor again, as the previous one is empty now.
    for doc in bag_of_words:
        # Values of the Mongo bag of words: row, column, value
        user = doc['_id']['user_id']
        word = doc['_id']['word']
        count = doc['value']

        M[(user_ids[user], words[word])] = count

    # Inversion of our data structures the dictionary (key, value) is duplicated into the same one with (value, key)
    # instead. This will be useful in the machine learning step.
    for i in words:
        words_indexes[words[i]] = i
    for i in user_ids:
        user_indexes[user_ids[i]] = i

    return M, words_indexes, user_indexes, user_ids, words


if __name__ == '__main__':


    np.set_printoptions(suppress=True)

    dbname = 'tweepoll_v2'
    client = MongoClient()
    db = client[dbname]

    # Getting the data in Python
    data = build_word_bag(dbname)
    bag_of_words = data[0]
    word_indexes = data[1]
    user_indexes = data[2]
    user_ids = data[3]
    words = data[4]

    # TF-IDF COMPUTATION
    # At the beginning we computed it roughly by going through all lines and columns. This was much too time consuming
    # Hence now we first compute global sums, and then compute the final value.

    # Computing the sum of words for each user
    nb_words_by_user = [sum(bag_of_words[i,:]) for i in range(bag_of_words.shape[0])]

    # Computing the number of documents that contain each word
    nb_users_by_word = [np.count_nonzero(bag_of_words[:,j]) for j in range(bag_of_words.shape[1])]

    # Computing the exact TF/IDF value, going through all the places
    for j in range(bag_of_words.shape[1]):
        for i in range(bag_of_words.shape[0]):
            value = bag_of_words[i,j]
            # Explanation of the TF/IDF formula available in the report
            new_value = value/nb_words_by_user[i] * np.log(bag_of_words.shape[0]/nb_users_by_word[j])
            bag_of_words[i,j] = new_value

    # Creation of the targets values. Not an obvious task as we need to align the bag of words with the right labels
    targets = np.zeros((bag_of_words.shape[0]))
    for id, index in user_ids.items():
        label = db.users.find({"_id": id})[0]['label']
        targets[index] = label

    # Make sure the dataset is correctly balanced between Hillary Clinton and Donald Trump
    # Indeed it appears that there are less voters for Hillary Clinton than Donald Trump
    # Hence to make sure our model has no bias toward one or the other we remove some Trump's observations
    nb_total = len(bag_of_words)
    bow_hillary = [bag_of_words[i] for i in range(nb_total) if targets[i] == 1]
    bow_trump = [bag_of_words[i] for i in range(nb_total) if targets[i] == 0]
    nb_hillary = len(bow_hillary)
    bow_trump = bow_trump[:nb_hillary]
    labels_final = [0 for i in range(nb_hillary)] + [1 for i in range(nb_hillary)]
    bow_final = bow_trump + bow_hillary

    # Serialization of our data: previous operations are very time consuming. Hence we did it once and afterwards used
    # the serialized objects for the learning
    import pickle
    with open("C:/data/serialized/bow.p", "wb") as f:
        pickle.dump(bag_of_words, f)
    with open("C:/data/serialized/user_indexes.p", "wb") as f:
        pickle.dump(user_indexes, f)
    with open("C:/data/serialized/user_ids.p", "wb") as f:
        pickle.dump(user_ids, f)
    with open("C:/data/serialized/words_indexes.p", "wb") as f:
        pickle.dump(word_indexes, f)
    with open("C:/data/serialized/words_ids.p", "wb") as f:
        pickle.dump(words, f)
    with open("C:/data/serialized/labels.p", "wb") as f:
        pickle.dump(targets, f)