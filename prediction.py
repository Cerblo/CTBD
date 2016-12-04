import pickle
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import numpy as np

with open("C:/data/serialized/lda.p", "rb") as f:
    lda = pickle.load(f)

with open("C:/data/serialized/bow_sample.p", "rb") as f:
    bow = pickle.load(f)

with open("C:/data/serialized/user_ids_sample.p", "rb") as f:
    user_ids = pickle.load(f)

predictions = lda.predict(bow)
sum(predictions)/len(predictions)