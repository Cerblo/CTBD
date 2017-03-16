from pymongo import MongoClient

from bson.code import Code
import time

client = MongoClient()
db = client['tweepoll_fr']



########################################################################

# Counting all words occurrences (collection all_words_count).
# This map reduce process is very similar to the one we know.
# The only difference is that it's implemented in Javascript, framework needed by MongoDB to run it

map = Code("""function(){
        var text = this.message
        var tweet_words = text.replace(/[^\w\s]|_/g, "").replace(/\s+/g, " ").replace(/[0-9]/g,"").toLowerCase().split(" ");

        for (var i = 0; i < tweet_words.length; i++) {
        emit(tweet_words[i], 1) ;
                                                    }
                        }
            """)

# The reduce step is just summing the values by key
reduce = Code("""function(key, values){
    var total = 0;

    for (var i=0; i < values.length; i++){
    total += values[i];}

    return total;}
    """)

db.tweets.map_reduce(map, reduce, "all_words_count")
# This query provides Mongo with the map and reduce functions,
# aside with the name of the new collection


#########################################################################
# Generating the actual bag of words values (collection words_occurrences_by_user)
# Almost the same process as the previous one, except that the emitted data are couples [(user_id, words),1]
# instead of just [words,1]

map_users = Code("""function(){

        var user = this.user_id
        var text = this.message
        var tweet_words = text.replace(/[^\w\s]|_/g, "").replace(/\s+/g, " ").replace(/[0-9]/g,"").toLowerCase().split(" ");

        for (var i = 0; i < tweet_words.length; i++) {
        emit({user_id:user, word: tweet_words[i]},1) ;
                                                    }
                        }
            """)

# The reduce step is just summing the values by key
reduce_users = Code("""function(key, values){
    var total = 0;

    for (var i=0; i < values.length; i++){
    total += values[i];}

    return total;}
    """)

db.tweets.map_reduce(map_users, reduce_users, "words_occurences_by_user")


################################################################################
# Create the final dictionary of words
# We filter the all_words_count by removing the stop words.
# Then we extract just the top 1,000.

# This query simulates an SQL 'join'
query = [
    {'$lookup':
         {  'from': 'stop_words',
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
    {'$limit': 5000}]

db.relevant_words.insert(db.all_words_count.aggregate(query))

###########################################################################
# Creation of the final dataset
# We filter the raw bag of words 'words_occurrences_by_user with the collection relevant words.
# We then get just a bag of words with those 5,000 words.

query = [
    {'$lookup':
         {  'from': 'relevant_words',
            'localField': '_id.word',
            'foreignField': '_id',
            'as': 'matched_docs'
            }
     },
    {'$match':
            {'matched_docs': {'$ne':[]}},
     },
    {'$project': {'_id':1, 'value':1}}
]

db.dataset.insert(db.words_occurences_by_user.aggregate(query))

