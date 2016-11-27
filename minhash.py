def file_extraction(path):
    """
     This function aims to extract the data from the json files downloaded from Git
    We go through all the files thanks to two loops (to distinguish numbers in 01, 02, 03 etc, and the 10, 11, 12 etc
    We create a list 'articles' containing all the bodies of the articles, and return the bag-of-words representation
    of this list

    :param path: path in the computer where those files are stored
    :return: bag-of-words representation of the data, topics of these articles.
            Returning the topics will be useful to analyse the consistency of the bucket at the end

    """
    from sklearn.feature_extraction.text import CountVectorizer
    import json

    articles = []
    topics = []
    for i in range(0, 10):
        filepath = path + 'file-number-' + str(0) + str(i)
        j = json.loads(open(filepath, 'r').read())

        for article in j:
            if 'body' in article.keys() and 'topics' in article.keys():
                articles.append(article['body'])
                topics.append(article['topics'])

    for i in range(10, 22):
        filepath = path + 'file-number-' + str(i)
        j = json.loads(open(filepath, 'r').read())
        for article in j:
            if 'body' in article.keys() and 'topics' in article.keys():
                articles.append(article['body'])
                topics.append(article['topics'])

    bag_of_words = CountVectorizer(min_df=0).fit_transform(articles)

    return bag_of_words, topics


def minHashAlgo(articles, n_articles, n_permutations):
    """ This function aims to implement the minHash algorithm
    Inputs :
    - articles : the list of all the articles texts under the bag of words representation
    - n_articles : nunmber of articles we want to exploit out of the whole list.
    - n_permutations : number of permutations we want to process

    Output: the minHash matrix, of shape (n_articles, n_permutations)
    - rows: articles
    - columns: permutations
    """

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.utils import shuffle
    import numpy as np

    bag_of_words = articles[:n_articles]

    minHash = np.zeros((n_articles, n_permutations))
    # We initialize the value of our minHash matrix with zeros. We will fill it afterwards

    buffer = bag_of_words
    # This variable will store the permuted matrix

    for i in range(n_permutations):
        buffer = shuffle(buffer.transpose()).transpose()
        # Permute the rows of set given in argument.
        # We use this transpose trick to keep our bag of words shape (articles in rows and words in columns)

        for j in range(buffer.shape[0]): # We go through all the rows of the permuted matrix

            minHash[j][i] = np.min(buffer[j].nonzero()[1]) # This instruction gives the value of the first value non zero.

    np.set_printoptions(suppress=True)

    return minHash


def minHashBuckets(minHash):

    """
    This function aims to calculates the buckets of our MinHash algorithm.

    Input : the minHash matrix, of shape (number of articles, number of permutations)
    """

    unique = []
    # Unique will stores the unique rows of our MinHash matrix.
    # Hence the number of elements of unique will be the number of buckets that we get.
    # This list will contains couples (row of the minHash matrix, row index where this unique row is found)
    # Thus unique is the list of all the buckets, including the value of the corresponding row

    for i in range(len(minHash)):

        added = False
        # This boolean allows us to control when a bucket of more than two rows is created
        # Indeed the majority of the buckets will consists just in one row

        for j in unique:
            if minHash[i].tolist() == j[0]:
                j[1].append(i)
                added = True

        if not added:
            unique.append((minHash[i].tolist(), [i]))

    buckets = [j[1] for j in unique if len(j[1]) > 1]
    # We list here only the buckets of more than 2 articles
    # Implicitly, the other rows are just in a bucket alone

    buckets = {buckets.index(j) + 1: j for j in buckets}
    # Buckets has now this aspect : { bucket_number : list of the articles belonging to this bucket }

    return buckets


if __name__ == "__main__":
    import time
    path = 'C:\\Users\\Wacim Belblidia\\Documents\\Cours DTU\\Computational tools for big data\\Weeks\\Week9\\'
    (articles, topics) = file_extraction(path)
    f = open('C:\\Users\Wacim Belblidia\Documents\Cours DTU\Computational tools for big data\Weeks\Week9\minhash_results.txt','w')

    for n_permutations in [3, 5, 10]:
        for n_articles in [100, 1000, 2000]:
            start = time.time()

            # n_permutations = 3
            # n_articles = 100 # Out of the 10,377 articles, we want to run MinHash only on 10,000 of them

            minHash = minHashAlgo(articles, n_articles, n_permutations)
            buckets = minHashBuckets(minHash)

            print('------------- MinHash Algorithm --------------')
            print('------ %d articles, %d permutations -------\n' % (n_articles, n_permutations))
            print('\n %d buckets contain more than one article: \n' % len(buckets))

            f.write('------------- MinHash Algorithm --------------\n')
            f.write(str(n_articles) + ' articles and ' + str(n_permutations) + ' permutations\n')
            f.write(str(len(buckets)) + ' buckets contain more than one article\n\n')


            wrong_semantic = [] # We will count the buckets with different topics.
            # It would be some missclassification

            for i in buckets:
                b = True
                print('Bucket %d' % i)
                f.write('Bucket ' + str(i) +'\n')
                top = topics[buckets[i][0]]

                for j in buckets[i]:
                    b=b and topics[j] == top
                    f.write(str(j) + ' ' + str(topics[j]) + '\n')
                    print(j, topics[j], articles[j])

                if not b:
                    wrong_semantic.append(i)

                print('\t')

            # f.write(str(n_articles)+ ' ' + str(n_permutations)+ ' ' + str(time.time() - start) + ' ' + str(len(buckets))+ ' '  + str(len(wrong_semantic))+'\n')

            print('\nAll the buckets have articles of the same topics : ' + str(wrong_semantic == []))
            print('Number of wrong buckets : %d' % len(wrong_semantic))
            print('Wrong buckets : '),print(wrong_semantic)
            print('\nTime of execution : %d seconds' % (time.time()-start))

            f.write('All the buckets have articles of the same topics : ' + str(wrong_semantic == []) +'\n')
            f.write('Number of wrong buckets : '+ str(len(wrong_semantic))+'\n')
            f.write('Wrong buckets : ' + str(wrong_semantic) + '\n')
            f.write('Time of execution : ' + str(time.time() - start) + 'seconds\n\n')