
def create_boolean(user_id, label,candidates):

    other_candidates = [i for i in candidates if i != label]
    b=False
    for j in other_candidates:

        b = b or api.show_friendship(source_id=user_id, target_id=candidates[j])[0].following

    return b

def insert_user_information(api_user, label, count):
    '''

    :param api_user: user object from twitter API
    :param label:0 or 1, depending on from which this user comes from (Hillary's list or Trump's list?)
    :param trump_id:
    :param clinton_id:
    :return:
    '''

    candidates={0:macron.id,1:lepen.id,2:hamon.id,3:fillon.id}

    user = {}
    user['_id'] = api_user.id
    
    b = create_boolean(user['_id'], label,candidates)

    # b is true if api_user is following the candidate label
    if not b and api_user.lang == 'fr':

        print('Start insertion process')
        user['location'] = api_user.location
        user['nb_tweets'] = api_user.statuses_count
        user['nb_followers'] = api_user.followers_count
        user['description'] = api_user.description
        user['label'] = label
        db.users.insert_one(user)
        insert_tweet_information(user['_id'])

        count += 1
        print('User has been inserted')
    return count


def insert_tweet_information(user_id):
    '''
    :param user_id:
    :return: return the ids of the tweets of this user.
    Also insert the object tweet to the MongoDB, for every tweet of this guy.

    '''

    import datetime
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    try:
        new_tweets = api.user_timeline(user_id=user_id, count=200)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # save the id of the oldest tweet less one. Exception can occur if the number of tweets is 0
        try:
            oldest = alltweets[-1].id - 1
        except IndexError:
            oldest=len(alltweets)
        # keep grabbing tweets until there are no tweets left to grab

        while len(new_tweets) > 0: # We retrieve all the tweets of that user until we reach the end

            # all subsequent requests use the max_id param to prevent duplicates
            new_tweets = api.user_timeline(user_id=user_id, count=200, max_id=oldest)

            # save most recent tweets
            alltweets.extend(new_tweets)
            # update the id of the oldest tweet less one
            try:
                oldest = alltweets[-1].id - 1
            except IndexError:
                pass
            print(' 200 tweets added')


        tweet_ids=[]

        for tweet in alltweets:

            tweet_object = {}
            tweet_object['_id'] = tweet.id
            tweet_object['user_id'] = user_id
            tweet_object['message'] = tweet.text
            tweet_object['hashtag'] = tweet.entities['hashtags']
            tweet_object['date'] = tweet.created_at

            db.tweets.insert(tweet_object)
        print('Total: %d tweets have been added' % len(alltweets))

        return tweet_ids
    except tweepy.error.TweepError:
        pass

def extract_information(label, nb_users):

    count = 0
    candidates={0:macron,1:lepen,2:hamon,3:fillon}


    while count < nb_users:

        followers = candidates[label].followers_ids()

        for user in followers:
            if count < nb_users:
                api_user = api.get_user(id=user)

                # Only the users which have more than 100 tweets are selected
                if api_user.statuses_count > 100:
                    count = insert_user_information(api_user, label, count)
                    print(count)
                # We delete the twitter object to make sure the RAM is not saturated
                del api_user
            else:
                break


if __name__ == "__main__":

    import logging
    import tweepy
    import time
    import logging
    from pymongo import MongoClient
    import json
    import numpy as np
    start=time.time()
    client = MongoClient()

    ## TO CHANGE
    db = client['tweepoll_fr']

    filename = "C:/token/access.json"
    with open(filename) as file:
        token = json.load(file)

    # Logging on the twitter API. This is mandatory to be able to use it
    auth = tweepy.OAuthHandler(token["consumer_key"], token["consumer_secret"])
    auth.set_access_token(token["access_key"], token["access_secret"])

    api = tweepy.API(auth, wait_on_rate_limit=True)



    macron = api.get_user('EmmanuelMacron')
    lepen = api.get_user('MLP_officiel')
    hamon = api.get_user('benoithamon')
    fillon = api.get_user('FrancoisFillon')

    candidates={0:'Macron',1:'LePen',2:'Hamon',3:'Fillon'}

    start_time = time.time()
    labels = [0,1,2,3]
    while 1:

        try:

            # This part makes sure that we can inform about the state of the process
            # even if we don't have access to our computer

            # Whenever the time elapsed is greater than an hour, a status is published on the twitter account
            # (defined by the token). This allows checking the process on our mobile phone
            # if time.time() - start_time > 7200:
            #     api.update_status('''US Information Extraction :\n Users in the base : %d
            #     \n Tweets in the base : %d \n ''' % (db.users.find().count(), db.tweets.find().count()))
            #     start_time = time.time()
            np.random.shuffle(labels)
            for label in labels:
                # Call the function that insert the given number of profiles in the database
                extract_information(label, 500)

        # This is the part that handles unpredicted errors
        # Retry after a minute but still print the stacktrace
        except Exception as e:
            logging.error(e, exc_info=True)
            print('I sleep')
            time.sleep(1)
            pass


    print(time.time() - start_time)