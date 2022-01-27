import tweepy
import pandas as pd
import re

# 트위터 앱의 Keys and Access Tokens 탭 참조(자신의 설정 값을 넣어준다)
consumer_key = ""
consumer_secret = ""

# 1. 인증요청(1차) : 개인 앱 정보 
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

access_token = ""
access_token_secret = ""

# 2. access 토큰 요청(2차) - 인증요청 참조변수 이용
auth.set_access_token(access_token, access_token_secret)

# 3. twitter API 생성  
api = tweepy.API(auth,wait_on_rate_limit=True)

keyword = "대한항공";     # 자신이 검색하고 싶은 키워드 입력 
search = [] # 크롤링 결과 저장할 변수   

cnt = 1
while(cnt <= 10):   # 10page 대상으로 크롤링
    tweets = api.search_tweets(keyword)
    for tweet in tweets:
        search.append(tweet)
    cnt += 1

# 원하는 정보만 저장 
# 날짜, 트윗 내용

def cleaning_text(df):
    '''
    cleaning_text() 함수: 특수문자 공백 반복적인 마침표 영어 대소문자 _ 제거 
            input parameter : (str)df
            output : (str)df
    '''
    
    while ('.' in df):
        df = df.replace('.', '')
    df = re.sub('[a-zA-Z-=+,#/\?:^$.@*\"※~&%ㆍ_!』\\‘|\(\)\[\]\<\>`\'…》]',' ', df)
    df = ' '.join(df.split()).rstrip()
    return df

tweet_list = [] 
con=[]

for i in (search): 
    '''
    username = i.id 
    favorites = i.favorite_count
    retweets = i.retweet_count
    '''
    tweet_date = i.created_at
    content = i.text 
    content = cleaning_text(content)
    #중복 내용 추가 X
    if content not in con:
        con.append(content)
        info_list = [tweet_date, content]   
        tweet_list.append(info_list)


df = pd.DataFrame(tweet_list, columns=['tweet_date','content'])

df.to_csv("C:/Users/82102/OneDrive/문서/Emotion-Recognization-fork/News_Crawling/NK/twitter_crawling.csv",header=True,index=False)