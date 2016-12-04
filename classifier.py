from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import RandomForestClassifier
import pickle
import warnings
import time
import numpy as np
warnings.filterwarnings("ignore", category=UserWarning)

# We have made a function for each classifier
def classifier_logistic(features, targets):
    '''
    Classifier for logistic regression. Ouput the score of the classifier and serialize the model as pickle
    :param features: bag of words representation of our users' tweets
    :param targets: labels of these users
    :return: score of the learning algorithm
    '''
    print('--------------- Logistic Regression ---------------')

    #Initialize the classifier, split the dataset into training and test, and fit the classifier
    lr = LogisticRegression()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)
    lr.fit(train_set,train_features)

    #Predict the labels on the test set
    prediction = lr.predict(test_set)

    #Calculate and display the score and the confusion matrix
    score = lr.score(test_set, test_features)
    print(score)
    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    print(A)
    print('Success: %f out of %d points' % (((A[0, 0] + A[1, 1]) / s), s))

    #Serialize the model as a pickle file
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/lr_v2.p", "wb") as f:
        pickle.dump(lr, f)

    #Return the score the prediction and the model
    return score, prediction, lr.coef_

def classifier_randomforest(features, targets):
    '''
    Classifier for random forest. Ouput the score of the classifier and serialize the model as pickle
    :param features: bag of words representation of our users' tweets
    :param targets: labels of these users
    :return: score of the learning algorithm
    '''
    print('--------------- RandomForest Classifier ---------------')

    #Initialize, split the dataset, fit the classifier and make the predictions
    lr = RandomForestClassifier()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)
    lr.fit(train_set,train_features)
    prediction = lr.predict(test_set)

    # Calculate and display the score and the confusion matrix for the classifier
    score = lr.score(test_set, test_features)
    print(score)
    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    print(A)
    print('Success: %f out of %d points' % (((A[0, 0] + A[1, 1]) / s), s))

    # Serialize the model
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/rf_v2.p", "wb") as f:
        pickle.dump(lr, f)

    # Return score and predictions
    return score, prediction


def classifier_lda(features, targets):
    """
    Classifier for Linear Discriminant analysis. Ouput the score of the classifier and serialize the model as pickle
    :param features: bag of words representation of our users' tweets
    :param targets: labels of these users
    :return: score of the learning algorithm
    """

    print('---------- LDA -------------')

    #Initialize, split, train and predict
    # We use the prior probabilities to make sure that even if we don't have exactly the same number of labels 1 and 0,
    # the prediction is not biased towards one or the other candidates
    lda = LinearDiscriminantAnalysis()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)
    lda.fit(train_set, train_features)
    prediction = lda.predict(test_set)

    # Display the confusion matrix along with the score
    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    print(A)
    print('Success: %f out of %d points' % (((A[0,0] + A[1,1])/s),s))

    lda = LinearDiscriminantAnalysis()
    lda.fit(features, targets)
    # Serialize the model
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/lda_v3.p", "wb") as f:
        pickle.dump(lda, f)

    return prediction

def classifier_qda(features, targets):
    """
    Classifier for Quadratic Discriminant analysis. Ouput the score of the classifier and serialize the model as pickle
    :param features: bag of words representation of our users' tweets
    :param targets: labels of these users
    :return: score of the learning algorithm
    """

    print('---------- QDA ------------')

    # Initialize, split the dataset, train and make predictions
    # We use the prior probabilities to make sure that even if we don't have exactly the same number of labels 1 and 0,
    # the prediction is not biased towards one or the other candidates
    qda = QuadraticDiscriminantAnalysis()
    train_set, test_set, train_features, test_features = train_test_split(features, targets, test_size=0.1)
    qda.fit(train_set, train_features)
    prediction = qda.predict(test_set)

    # Display the confusion matrix and the score of the prediction
    A = confusion_matrix(test_features, prediction)
    s = np.sum(A)
    print(A)
    print('Success: %f out of %d points' % (((A[0,0] + A[1,1])/s),s))

    qda = QuadraticDiscriminantAnalysis()
    qda.fit(features, targets)
    # Serialize the model
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/qda_v2.p", "wb") as f:
        pickle.dump(qda, f)

    return prediction





# Main method of the module
# Call all the classifiers and print their outputs as well as their execution times to compare them
if __name__ == '__main__':

    #Allows a nicer output
    np.set_printoptions(suppress=True)

    # Deserialize all objects that we need to make the training
    # The first one is the bag of words which is our predictors dataset
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/bow_v2.p", "rb") as f:
        bag_of_words = pickle.load(f)
    # Labels of the dataset
    with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/labels_v2.p", "rb") as f:
        targets = pickle.load(f)

    # Logistic Regression
    start = time.time()
    score, prediction, coef = classifier_logistic(bag_of_words, targets)
    print('Logistic Regression in %f s' % (time.time() - start))

    # Linear Discriminant analysis
    start = time.time()
    prediction = classifier_lda(bag_of_words, targets)
    print('LDA in  %f s' % (time.time() - start))
    start = time.time()

    # Quadratic Discriminant analysis
    prediction = classifier_qda(bag_of_words, targets)
    print('QDA: %f' % (time.time() - start))

    # Random Forest Classifier
    start = time.time()
    prediction = classifier_randomforest(bag_of_words, targets)
    print('Random Forest in %f s' % (time.time() - start))