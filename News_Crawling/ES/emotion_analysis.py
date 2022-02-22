import pandas as pd
from konlpy.tag import Mecab
import numpy as np
from collections import Counter # 단어 빈도수를 세기 위한 모듈

'''
    Emotion_Analysis :: 감성사전 구축을 위한 class
'''


class Emotion_Analysis:
    def __init__(self):
        '''
        __init__() : 초기화 함수
                    특정 기업 price data 및 new data load
        '''

        # news data & price data load
        self.news = pd.read_csv('News_Crawling/ES/[엔씨소프트]news_data.csv')
        self.price = pd.read_csv('News_Crawling/ES/[엔씨소프트] price_labeling.csv')
        
        # print('News data info')
        # print(self.news.info())

        # emotion dict
        self.word_list = []
    
    def set_columns(self):
        '''
        set_columns() : news data의 column을 생성
            input parameter : None
                현재 news data의 column은 data로 구성되어 있음
            output : 각 column이 Date, Title, Content로 이루어진 news data
        '''

        data1 = self.news.columns
        self.news.columns = ['Date', 'Title', 'Content']
        self.news.loc[self.news.shape[0]] = data1

        print('Changed News Data info')
        print(self.news.info())


    def remove_keyword(self, content):
        '''
        remove_keyword() : 형태소 분석 전 keyword인 기업명 제외하기
                            apply 함수를 적용하기 위함
        '''
        keyword = '엔씨소프트'
        return content.replace(keyword, "")

    
    def extract_NV(self, word):
        '''
        extract_NV() : tag 중 N(명사), V(동사)로 시작하는 tag만을 추출
                        apply 함수를 적용하기 위함
        '''
        if word[1][0] == 'N' or word[1][0] == 'V':
            return word

    def build_word(self, content):
        '''
        build_word() : 형태소 분석 - tag 추출
                        extract_NV 함수를 호출함으로써 tag 중 명사와 동사에 해당하는 단어 tag 쌍만을 저장
                        apply 함수를 적용하기 위함
        '''
        mecab= Mecab()
        words = pd.Series(mecab.pos(content))
        word_list = []
        word_list.append(words.apply(self.extract_NV))
        return word_list

    
    def content_tag(self):
        '''
        content_tag() : 전체 감성분석 함수
                        -> news content의 형태소 분석
        '''

        # news data column 설정
        self.set_columns()

        # content column만 추출
        # self.contents = self.news.loc[:, 'Content']

        # content 중 기업명 제외하기 - apply 함수 사용
        self.news['Content'] = self.news['Content'].apply(self.remove_keyword)
        

        ### [version 1] ###
        # 동사, 형용사, 명사만을 words에 추가
        self.news['Word'] = self.news['Content'].apply(self.build_word)
        
        # counts로 빈도수 저장
        '''
        for문 안 쓰려는 욕심을 가지고 계속 코드를 짜고 있는데 너모나도 신경쓸게 많아졌다 !!
        아효....
        '''

        ### [version 2] ###
        # 1. 동사, 형용사, 명사만을 words에 추가
        # 2. [불용어 처리] 1) LEN 1 제외
        mecab  = Mecab()
        for idx in range(len(self.news['Content'])):
            mecab_tag = mecab.pos(self.news['Content'][idx])
            for tagg in mecab_tag:
                if (tagg[1][0] == 'N' or tagg[1][0] == 'V') and (len(tagg[0]) != 1):
                    self.word_list.append(tagg[0])
        

        # 불용어 처리
        '''
            불용어 처리
                이미 해본 방식 :: 1) LEN 1 제외, 2) 한글 불용어 100에 있는 단어 제외
                1) LEN 1 제외 -- 완료
                2) 한글 불용어 100 파일이 어디에 있는거야 !!?
        '''

        # 각 단어의 빈도수를 내림차순으로 저장
        self.word_freq = Counter(self.word_list).most_common()
        print('\nWord & Frequency')
        print(self.word_freq)
        print('\n')

        # 유니크한 단어가 몇개 나오는지 출력
        print("\nThe number of Unique words :", len(np.unique(self.word_list)))
        print('\n')




if __name__ == "__main__":
    '''
    Crawling class 실행
    '''

    # crawling class 선언
    EA = Emotion_Analysis()
    
    # 형태소 분석
    EA.content_tag()