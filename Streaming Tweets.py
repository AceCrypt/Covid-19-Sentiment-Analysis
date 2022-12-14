from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import twitter_creds
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
from textblob import TextBlob
import re


## Twitter Client ##
class TwitterClient():
    def __init__(self,twitter_user=None):
        self.auth = TwitterAuth().auth_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get__user_timeline_tweets(self,num_tweets):
        my_tweets = []

        for tweet in Cursor(self.twitter_client.user_timeline,id=self.twitter_user).items(num_tweets):
            my_tweets.append(tweet)
            return my_tweets

    def get_friend_list(self,num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends,id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self,num_tweets):
        home_timeline = []
        for tweets in Cursor(self.twitter_client.home_timeline,id=self.twitter_user).items(num_tweets):
            home_timeline.append(tweets)
        return home_timeline

    def get_twitter_client_api(self):
        return self.twitter_client



## Twitter Authenticator##
class TwitterAuth():

    def auth_twitter_app(self):
        auth = OAuthHandler(twitter_creds.CONSUMER_KEY,twitter_creds.CONSUMER_KEY_SECRET)
        auth.set_access_token(twitter_creds.ACCESS_TOKEN,twitter_creds.ACCESS_TOKEN_SECRET)
        return auth



class TwitterStreamer():
    def __init__(self):
        self.Twitter_auth = TwitterAuth()


    def stream_tweets(self,fetched_tweets,hash_list):
       listener = TwitterListener(fetched_tweets) 
       auth = self.Twitter_auth.auth_twitter_app()   
       stream = Stream(auth,listener)
       stream.filter(track=hash_list) 


class TwitterListener(StreamListener):
    def __init__(self,fetched_tweets):
        self.fetched_tweets = fetched_tweets

    def on_data(self,data):
        try:
            print(data)
            with open(self.fetched_tweets,'a') as tf:
                tf.write(data)
        
            return True
        except BaseException as e:
            print("Error on data: %s" % str(e))
        return True


    def on_error(self,status):
        if status ==420:
            # to stop exceeding rate twitter rate limit #
            return False
        print(status)

class TweetAnalyser():

    def clean_tweet(self,tweet):
        return " ".join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",tweet).split())


    def analyze_sentiment(self,tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return "Positive"
        elif analysis.sentiment.polarity == 0:
            return "Neutral"
        else:
            return "Negative"



    def tweets_to_dataframe(self,tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets],columns = ['tweet'])
        #pd.set_option('display.max_colwidth', -1)
        df['id'] = np.array([tweet.id for tweet in tweets ])
        df['len'] = np.array([len(tweet.text) for tweet in tweets ])
        df['source'] = np.array([tweet.source for tweet in tweets ])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets ])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets ]) 
        df['date'] = np.array([tweet.created_at for tweet in tweets ])


        return df

if __name__ == '__main__':

    #hash_list = ['covid-19','corona','lockdown']
    #fetched_tweets = 'tweets.json'

    #twitter_streamer = TwitterStreamer()
    #twitter_streamer.stream_tweets(fetched_tweets,hash_list)


    #twitter_client = TwitterClient('realdonaldTrump')
    #rint(twitter_client.get__user_timeline_tweets(5))
#####################################################################
    twitter_client = TwitterClient()
    api = twitter_client.get_twitter_client_api()
    tweet_anal = TweetAnalyser()
    
    tweets = api.user_timeline(screen_name='realdonaldTrump',count=20000) 
    #print(dir(tweets[0]))
    #print(tweets[0].author)
    df = tweet_anal.tweets_to_dataframe(tweets)
    df['sentiment'] = np.array([tweet_anal.analyze_sentiment(tweet) for tweet in df['tweet'] ])


    print(df.head(5))

    # Get average length over all tweets

    print("The average length of all tweets is {}".format(+np.mean(df['len'])))

    # numer of likes on most likes

    print("The number of likes on most liked tweet is {}".format(np.max(df['likes'])))

    # Time Series Plotting

    time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(16,4),label = 'likes',legend=True)

    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize=(16,4),label = 'retweets',legend=True)
    plt.show()















  

    


    

