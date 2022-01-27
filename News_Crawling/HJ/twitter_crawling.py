from os import access
import json
import twitter
import tweepy

class Twit:
    def __init__(self):
      
        with open('./DATA/config.json','r') as in_file:
            config = json.load(in_file)
            twitter_consumer_key = config['twitter_consumer_key']
            twitter_consumer_secret = config['twitter_consumer_secret']
            twitter_access_token = config['twitter_access_token']
            twitter_access_secret = config['twitter_access_secret']

        self.twitter_api = twitter.Api(consumer_key = twitter_consumer_key,
                                consumer_secret = twitter_consumer_secret,
                                access_token_key = twitter_access_token,
                                access_token_secret = twitter_access_secret)

        auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
        auth.set_access_token(twitter_access_token, twitter_access_secret)

        self.tweepy_api = tweepy.API(auth)

    def twitter_crawling_example(self):
        
        #query = "에프앤에프"
        #statuses = twit.twitter_api.GetSearch(term=query, count = 100)
        #for status in statuses:
        #    print(status.text)

        for tweet in tweepy.Cursor(twit.tweepy_api.search_tweets,
                                    q = "삼성전자 -filter:retweets",
                                    lang="ko").items(10):
            print(tweet.text)                           

if __name__ == "__main__" :
    twit = Twit()
    twit.twitter_crawling_example()
    

