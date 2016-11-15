
def insert_user_information(api_user, count):
    '''

    :param api_user: user object from twitter API
    :param trump_id:
    :param clinton_id:
    :return:
    '''


    user = {}
    user['id'] = api_user.id
    insert_tweet_information(user['id'])
    user['location'] = api_user.location
    user['nb_tweets'] = api_user.statuses_count
    user['nb_followers'] = api_user.followers_count
    user['description'] = api_user.description
    db.users.insert_one(user)
    count += 1
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
        print('tweets has been added')
        return tweet_ids
    except tweepy.error.TweepError:
        return []


def extract_information(nb_users):

    count = 0


    while count < nb_users:

        followers = twitter_account.followers_ids()

        for user in followers:
            if count < nb_users:
                api_user = api.get_user(id=user)
                print("test user")

                if len(api_user.location)>0 \
                    and api_user.statuses_count > 100 \
                    and not (api_user.time_zone is None) \
                    and 'US' in api_user.time_zone \
                    and api_user.lang == 'en'\
                    and not [i for i in db.users.find({'id':user})]:
                        print('Start insertion process')
                        count = insert_user_information(api_user, count) # Condition inserted inside
                else:
                    print('Irrelevant user')
            else:
                break


if __name__ == "__main__":

    import tweepy
    import time
    import logging
    from pymongo import MongoClient

    client = MongoClient()

    db = client['tweepoll']



    consumer_key = 'ypTAEHgMMp3WQ52nU83ReQag9'
    consumer_secret = 'iO1NG5Ce3uOnKj3GNxtFnZ8RwGxnP8j7iRJzNX96qEwFRWmmCj'
    api_key = '796514522731282432-7OJ8dNbYPeKyWjk3OCMLEy35GcfPI4G'
    api_secret = 'Xtip4LYSP4dUDsiNOcG9HxRbJjIZ8HnLN2aPz2PqIqA2W'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(api_key, api_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)


    twitter_account = api.get_user('Twitter')


    while 1:  # Boucle boucle boucle
        try:
            extract_information(100)
        except Exception as e:
            logging.error(e, exc_info=True)
            time.sleep(60)
            pass
