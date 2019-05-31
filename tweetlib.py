import tweepy
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import models
from textblob import TextBlob
import twitter_credentials
import json

GLOBAL=[]
class listener(StreamListener):
    def on_data(self, data):
        try:
            j=json.loads(data)
            if ('text' in j):
                t=TextBlob(j['text'])
                GLOBAL.append([(t.lower(),t.sentiment.polarity,t.sentiment.subjectivity)])
#                print((t.lower(),t.sentiment.polarity,t.sentiment.subjectivity))
                print (len(GLOBAL))
                return []
        except tweepy.error.TweepError:
            return []
    def on_error(self, status):
        print (status)


class TwitterClient():
    def __init__(self):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

    def get_user_timeline_tweets(self, num_tweets, handle):
        tweets = []
        try:
            t=Cursor(self.twitter_client.user_timeline, id=handle)
            for tweet in t.items(num_tweets):
                t=TextBlob(tweet._json['text'])
            #print (t.lower(), t.sentiment)
                tweets.append([t.lower(),t.sentiment.polarity,t.sentiment.subjectivity])
            return tweets
        except tweepy.error.TweepError:
            return []
    
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth
        
class TwitterStreamer():
    """
For streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
    
    def stream_tweets(self, value):
        auth = self.twitter_authenticator.authenticate_twitter_app()
        twitterStream = Stream(auth, TwitterListener("tweets.json"),tweet_mode='extended')
#        print ("track="+value)
        twitterStream.filter(track=[value],is_async=True)


class TwitterListener(StreamListener) :
    """
Basic Listener class that prints received tweets to Twitter
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
    def process_tweets(self):
        tweets=[]
        with open(self.fetched_tweets_filename, 'r') as tf:
            data=tf.read()
            try:
                j=json.loads(data)
                if ('text' in j):
                    t=TextBlob(j['text'])
                    if ((t.lower(),t.sentiment.polarity,t.sentiment.subjectivity,j['created_at']) not in tweets):
                        tweets.append((t.lower(),t.sentiment.polarity,t.sentiment.subjectivity,j['created_at']))
#                    print (len(tweets))
            except json.decoder.JSONDecodeError:
                pass

        return tweets

    def on_data(self, data):
        try:
#            print(data)
            with open(self.fetched_tweets_filename, 'w') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on data: %s" % str(e))
        return True

    def on_error(self, status) :
        if status == 420:
            return False
        print(status)



