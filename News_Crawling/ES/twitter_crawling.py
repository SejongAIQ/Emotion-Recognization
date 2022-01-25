import twitter
import json
import csv
import pandas as pd


class Twitter:
    def __init__(self):
        '''
        __init__() : 초기화 함수
                    토큰 저장 및 트위터 api 라이브러리 불러오기
        '''

        # 토큰
        self.twitter_consumer_key = "b4ycyDjRLpEgk9hOqDZDATBAv"
        self.twitter_consumer_secret = "3mKV79bbIqBt9dm2h5mszocja35D5lu8yEIS7nQhLpt6mxzB6B"  
        self.twitter_access_token = "1485890023614730242-9YcWGpLCj27itSqYvkQx1lEkVVafe5"
        self.twitter_access_secret = "55gXs0L5du5u6Sq8StEpQcYsIQqE0VNdq83tSGhJyAd1U"

        self.twitter_api = twitter.Api(consumer_key=self.twitter_consumer_key,
                                consumer_secret=self.twitter_consumer_secret, 
                                access_token_key=self.twitter_access_token, 
                                access_token_secret=self.twitter_access_secret)

        # self.tweet_data = pd.DataFrame(columns={"date", "tweet", "tag"})  
        self.tweet_data = pd.DataFrame(columns={"tweet", "tag"})  


    def search(self, keyword):
        '''
        search() : 특정 키워드 트윗 검색
            input parameter : keyword(str)
            output : 키워드 중심으로 crawlinge된 tweet csv파일
        '''
        query = keyword
        statuses = self.twitter_api.GetSearch(term=query, count=100)

        for status in statuses:
            tag_list = []
            for tag in status.hashtags:
                print(tag.text) # 태그
                tag_list.append(tag.text)

            print(status.text)
            tweet_text = status.text # 트윗
            # self.tweet_data.append(status.text) 


            
            # tweet_dict = {"data":date, "tweet":tweet_text, "tag":tag}
            tweet_dict = {"tweet":tweet_text, "tag":tag_list}
            self.tweet_data = self.tweet_data.append(tweet_dict, ignore_index=True)
        

        # csv로 변환
        tweet_df = pd.DataFrame(self.tweet_data)
        tweet_df.to_csv(keyword+"_tweet_data.csv", index=False, header=True)
    

    def streaming(self, keyword):
        '''
        streaming() : 특정 키워드가 포함된 트윗을 “실시간”으로 수집
            input parameter : keyword(str)
            output : streaming file (txt)
        '''

        query = [keyword]
        output_file_name = keyword+"_stream_result.txt"

        with open(output_file_name, "w", encoding="utf-8") as output_file:
            stream = self.twitter_api.GetStreamFilter(track=query)
        while True:
            for tweets in stream:
                tweet = json.dumps(tweets, ensure_ascii=False)
                print(tweet, file=output_file, flush=True)

    def json_to_csv(self, input_file, output_file):
        '''
        json_to_csv() : json파일을 csv로 변환
            input parameter : input_file name(txt), output_file name (csv)
                                ex) input_file = "data.txt", output_file = "data.csv"
            output : update csv file
        '''

        with open(input_file, "r", encoding="utf-8", newline="") as input_file, \
                open(output_file, "w", encoding="utf-8", newline="") as output_file:

            data = []
            for line in input_file:
                datum = ujson.loads(line)
                data.append(datum)
                
            csvwriter = csv.writer(output_file)
            csvwriter.writerow(data[0].keys())
            for line in data:
                csvwriter.writerow(line.values())

        

if __name__ == "__main__":
    '''
    twitter crawling 진행
    '''

    # twitter crawling class 선언
    tweet = Twitter()
    
    # keyword 검색
    '''
    추후에 keyword가 담겨있는 파일을 열어 Keyword 하나씩 받아오는 형식으로 진행
    '''
    keyword = '엔씨소프트주식'
    tweet.search(keyword)
