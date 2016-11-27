from pymongo import MongoClient

from bson.code import Code
import time

client = MongoClient()
db = client['work_db']

client = MongoClient()
db = client['work_db']

start = time.time()

map = Code("""function(){
        var text = this.message
        var tweet_words = text.replace(/[^\w\s]|_/g, "").replace(/\s+/g, " ").replace(/[0-9]/g,"").toLowerCase().split(" ");

        for (var i = 0; i < tweet_words.length; i++) {
        emit(tweet_words[i], 1) ;
                                                    }
                        }
            """)

reduce = Code("""function(key, values){
    var total = 0;

    for (var i=0; i < values.length; i++){
    total += values[i];}

    return total;}
    """)

db.tweets.map_reduce(map, reduce, "all_words_count")

print('All_words_count collection created in %f' % (time.time() - start))

start = time.time()
map_users = Code("""function(){

        var user = this.user_id
        var text = this.message
        var tweet_words = text.replace(/[^\w\s]|_/g, "").replace(/\s+/g, " ").replace(/[0-9]/g,"").toLowerCase().split(" ");

        for (var i = 0; i < tweet_words.length; i++) {
        emit({user_id:user, word: tweet_words[i]},1) ;
                                                    }
                        }
            """)

reduce_users = Code("""function(key, values){
    var total = 0;

    for (var i=0; i < values.length; i++){
    total += values[i];}

    return total;}
    """)

db.tweets.map_reduce(map_users, reduce_users, "words_occurences_by_user")

print('Words_occurences_by_user collection created in %f' % (time.time() - start))

query = [
    {'$lookup':
         {  'from': 'dictionary',
            'localField': '_id',
            'foreignField': '_id',
            'as': 'matched_docs'
            }
     },
    {'$match':
            {'matched_docs': {'$eq':[]}}
     },
    {'$project':
         {'_id':1, 'value':1}},
    {'$sort': {'value':-1}},
    {'$limit': 1000}]

db.relevant_words.insert(db.all_words_count.aggregate(query))

########################
# get words which belong to one of the two dictionary
query = [
    {'$lookup':
         {  'from': 'dictionary',
            'localField': '_id.word',
            'foreignField': '_id',
            'as': 'matched_docs'
            }
     },
    {'$lookup':
         {  'from': 'relevant_words',
            'localField': '_id.word',
            'foreignField': '_id',
            'as': 'matched_docs2'
            }
     },
    {'$match':
         {'$or':
            [{'matched_docs': {'$ne':[]}},
            {'matched_docs2': {'$ne':[]}}]
          }
     },
    {'$project': {'_id':1, 'value':1}}
]

db.dataset.insert(db.words_by_user.aggregate(query))


#############################
#take all words which are used a lot
