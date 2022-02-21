## Module import 
from ast import keyword
import pandas as pd
import numpy as np
from konlpy.tag import Mecab, Okt
import re
from make_stopword import words as stopword
from itertools import chain

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
        '''
            - merge_news() : csv에 있는 모든 문자열을 하나로 만드는 함수

                - input parameter : (array)title_list 
                - output : (str)string
        '''
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

        titles = mecab.pos(titles)
        titles_tmp = []
        for t in titles:
            if t[1].startswith(('V', 'N')):
                titles_tmp.append(t[0])

        titles_del_stop = [t for t in titles_tmp if t not in stopword]
        titles_del_stop = [t for t in titles_del_stop if len(t) > 1]

        # print(len(titles), len(set(titles))) # 2608 / 중복 제외 단어 개수 : 483

        # 기사 제목에서 명사만 추출
        titles_df = pd.Series(titles_del_stop) 
        # [ 단어, 빈도수 ] 구성으로 Dataframe 화
        titles_df = titles_df.value_counts().rename_axis('word').reset_index(name='count')

        # 빈도수 상위 25% 단어 추출
        num1to4 = int(len(set(titles_del_stop)) / 4)
        title_df_make_stopword = list(titles_df['word'][:num1to4])

        f = open(f'./Data/{KEYWORD}_title.txt', 'w')

        for word in title_df_make_stopword:
            f.write(word + '\n')

        f.close()
        # print(titles_df.head(10)) # 빈도수 상위 10개 출력

        #-------------------------------------------------------#

        # 뉴스 '내용' 합치고 문자영 cleaning
        contents = self.merge_news(data['contents']) 
        contents = self.string_cleaning(contents)

        contents = mecab.pos(contents)

        contents_tmp = []
        for t in titles:
            if t[1].startswith(('V', 'N')):
                contents_tmp.append(t[0])

        contents_del_stop = [t for t in contents_tmp if t not in stopword]
        contents_del_stop = [t for t in contents_del_stop if len(t) > 1]

        # print(len(contents_del_stop), len(set(contents_del_stop))) # 58293 / 중복 제외 단어 개수 : 3139
        
        # 기사 내용에서 명사만 추출 
        contents_df = pd.Series(contents_del_stop) 
        # [ 단어, 빈도수 ] 구성으로 Dataframe 화
        contents_df = contents_df.value_counts().rename_axis('word').reset_index(name='count') 

        # 빈도수 상위 25% 단어 추출
        num1to4 = int(len(set(contents_del_stop)) / 4)
        contents_df_make_stopword = list(contents_df['word'][:num1to4])

        f = open(f'./Data/{KEYWORD}_contents.txt', 'w')

        for word in contents_df_make_stopword:
            f.write(word + '\n')

        f.close()
        # print(contents_df.head(10))


if __name__ == '__main__':

    nlp = NLP()

    data = pd.read_csv('./Data/news_crawling.csv')
    KEYWORD = 'SD바이오센서'
    

    sample = ['에스디', '바이오', '센서', '에스디바이오센서', 'SD바이오센서', '에스', '디', '만', '억', '조']
    for s in sample:
        stopword.append(s)

    nlp.mecab_news(data)





