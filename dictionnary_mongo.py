filename = 'C:\\Users\Wacim Belblidia\Documents\Cours DTU\Computational tools for big data\Final project\\final scripts\stop_words.txt'
f = open(filename,'r').read().split(',')

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
client = MongoClient()
db = client['work_db']

for word in f:
    print(word)
    w = {}
    w['_id'] = word
    try:
        db.stop_words.insert_one(w)
    except DuplicateKeyError:
        pass
