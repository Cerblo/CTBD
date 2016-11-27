filename = 'C:\\Users\Wacim Belblidia\Documents\Cours DTU\Computational tools for big data\Final project\\final scripts\words.txt'
f = open(filename,'r').read().split('\n')

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
client = MongoClient()
db = client['english_dictionnary']

for word in f:
    print(word)
    w = {}
    w['_id'] = word
    try:
        db.words.insert_one(w)
    except DuplicateKeyError:
        pass
