## Module import 
import pandas as pd
import numpy as np
from konlpy.tag import Mecab, Okt
import re
from make_stopword import words as stopword

class NLP:

    def __init__(self):
        pass

    def string_cleaning(self, string):
        '''
            - string_cleaning() : string에 있는 특수 문자 제거 

                - input parameter : (str)string 
                - output : (str)cleanging string
        '''
        result = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', ' ', string)
        result = ' '.join(result.split()).rstrip()

        return result
    
    def merge_news(self, title_list):
        titles = ''
        for t in title_list:
            titles += t
        
        return titles
    
    def mecab_news(self, data):

        # 형태소 분석기 불러오기
        mecab = Mecab()

        # 뉴스 '제목' 합치고 문자열 cleaning
        titles = self.merge_news(data['title'])
        titles = self.string_cleaning(titles)

        titles = mecab.nouns(titles)
        titles_ex_stop = [t for t in titles if t not in stopword]
        ex_stop = [t for t in titles if t in stopword]

        print(len(titles), len(set(titles))) # 2608 / 중복 제외 단어 개수 : 483
        print(len(titles_ex_stop), len(set(titles_ex_stop))) # 2461 / 중복 제외 단어 개수 : 463

        titles_df = pd.Series() # 기사 제목에서 명사만 추출
        print(titles_df.value_counts().head(10)) # 빈도수 상위 10개 출력

        # 뉴스 '내용' 합치고 문자영 cleaning
        contents = self.merge_news(data['contents']) 
        contents = self.string_cleaning(contents)

        contents_df = pd.Series(mecab.nouns(contents)) # 기사 내용에서 명사만 추출

        # [ 단어, 빈도수 ] 구성으로 Dataframe화
        contents_df = contents_df.value_counts().rename_axis('word').reset_index(name='count') 
        # contents_df = pd.DataFrame(contents_df.value_counts(), columns={'word', 'count'})

        print(contents_df.head(10))

        # unique_word = contents_df.unique()
        # for i in unique_word:
        #     print(i, sep=',')

    def okt_news(self, data):
        
        # 형태소 분석기 불러오기
        okt = Okt()

        # 뉴스 '제목' 합치고 문자열 cleaning
        titles = self.merge_news(data['title'])
        titles = self.string_cleaning(titles)

        titles_df = pd.Series(okt.phrases(titles))
        # print(titles_df.value_counts().head(10))

        # 뉴스 '내용' 합치고 문자영 cleaning
        contents = self.merge_news(data['contents']) 
        contents = self.string_cleaning(contents)

        contents_df = pd.Series(okt.phrases(contents)) # 기사 내용에서 명사만 추출

        # [ 단어, 빈도수 ] 구성으로 Dataframe화
        contents_df = contents_df.value_counts().rename_axis('word').reset_index(name='count') 

        print(contents_df.head(10))

if __name__ == '__main__':

    nlp = NLP()

    data = pd.read_csv('./Data/news_crawling.csv')

    nlp.mecab_news(data)
    # nlp.okt_news(data)



