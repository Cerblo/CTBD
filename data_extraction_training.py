
def insert_user_information(api_user, label, count):
    '''

    :param api_user: user object from twitter API
    :param label:0 or 1, depending on from which this user comes from (Hillary's list or Trump's list?)
    :param trump_id:
    :param clinton_id:
    :return:
    '''

    candidates = {0:trump.id, 1:clinton.id}

    user = {}
    user['id'] = api_user.id
    b = api.show_friendship(source_id=user['id'], target_id=candidates[1-label])[0].following

    if not b and api_user.lang == 'en' and not [i for i in db.users.find({'id': user['id']})]:

        print('Start insertion process')
        insert_tweet_information(user['id'])
        user['location'] = api_user.location
        user['nb_tweets'] = api_user.statuses_count
        user['nb_followers'] = api_user.followers_count
        user['description'] = api_user.description
        user['label'] = label
        db.users.insert_one(user)
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


        tweet_ids=[]

        for tweet in alltweets:
            tweet_ids.append(tweet.id)

            tweet_object = {}
            tweet_object['tweet_id'] = tweet.id
            tweet_object['user_id'] = user_id
            tweet_object['message'] = tweet.text
            tweet_object['hashtag'] = tweet.entities['hashtags']
            tweet_object['date'] = tweet.created_at

            db.tweets.insert(tweet_object)
        print('%d tweets has been added' % len(tweet_ids))
        return tweet_ids
    except tweepy.error.TweepError:
        return []


def extract_information(label, nb_users):

    count = 0
    candidates = {0:trump, 1:clinton}


    while count < nb_users:

        followers = candidates[label].followers_ids()

        for user in followers:
            if count < nb_users:
                api_user = api.get_user(id=user)
                # print(api_user.name, api_user.location, api_user.statuses_count, api_user.time_zone,api_user.lang)

                # Here the location is not filtered, as we want more data and to do a Twitter poll
                if api_user.statuses_count > 100:
                    count = insert_user_information(api_user, label, count) # Condition inserted inside
                    print(count)
            else:
                break


if __name__ == "__main__":
    import logging
    import tweepy
    import time
    import logging
    from pymongo import MongoClient
    start=time.time()
    client = MongoClient()

    db = client['tweepoll']



    consumer_key = 'JcT9eaN3Fc3f9POcFXF4F2wIM'
    consumer_secret = 'OkpbxaK7e1epLyhZalzdvSlAJMf1O99F3F4wTmGscfzS85ZI82'
    api_key = '792840280848343042-UZ6JqLW0jHbYdPo2h0ODQtS1gdsYJwN'
    api_secret = 'CpnWsqioUGqrrQTkWTxKEHWNsxXmrN1wkRx8O5ELR8mzF'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(api_key, api_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    trump = api.get_user('realDonaldTrump')
    clinton = api.get_user('HillaryClinton')

    candidates={False:'Trump', True:'Clinton'}
    # Trump retrieve
    label = False

    while 1:
        try:
            extract_information(label, 5000)
        except Exception as e:
            logging.error(e, exc_info=True)
            print('I sleep')
            time.sleep(60)

            pass

    print(time.time()-start)