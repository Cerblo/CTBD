import pickle
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np

with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/lda_v3.p", "rb") as f:
    lda = pickle.load(f)

with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/bow_sample.p", "rb") as f:
    bow = pickle.load(f)

with open("C:/Users/Hippolyte/PycharmProjects/untitled/project/shared/user_ids_sample.p", "rb") as f:
    user_ids = pickle.load(f)

predictions = lda.predict(bow)
sum(predictions)/len(predictions)