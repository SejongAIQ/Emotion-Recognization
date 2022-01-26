from operator import index
from config import ACCESS_TOKEN, ACCESS_TOKEN_SECRET, API_KEY, API_KEY_SECRET
import pandas as pd
import re
import twitter

def string_cleaning(string):
    result = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', ' ', string)
    result = ' '.join(result.split()).rstrip()
    return result

twitter_api = twitter.Api(consumer_key=API_KEY,
                          consumer_secret=API_KEY_SECRET, 
                          access_token_key=ACCESS_TOKEN, 
                          access_token_secret=ACCESS_TOKEN_SECRET)

query = '에스디바이오센서'

data = pd.DataFrame(columns={'count', 'tweets'})
tweets_list = twitter_api.GetSearch(term = query, count = 1000)

a = 0

l = []

for tweet in tweets_list:
    for t in tweet.hashtags:
        l.append(t.text)

    text = string_cleaning(tweet.text)
    tmp = {'count': a, 'tweets': text}
    
    a += 1
    data = data.append(tmp, ignore_index=True)

print(l)
data.to_csv('example.csv', index=None, header=True)
