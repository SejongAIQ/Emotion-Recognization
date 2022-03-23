from soynlp.noun import LRNounExtractor
from soynlp.noun import NewsNounExtractor
import pandas as pd
from konlpy.tag import Mecab
import numpy as np
from collections import Counter # 단어 빈도수를 세기 위한 모듈

'''
    preprocessing_soynlp :: soynlp로 명사 추출 (태깅 작업)
'''


class preprocessing_soynlp:
    def __init__(self):
        '''
        __init__() : 초기화 함수
                    특정 기업 price data 및 new data load
        '''

        # news data & price data load
        self.news = pd.read_csv('News_Crawling/ES/[엔씨소프트]news_data.csv')
        # self.price = pd.read_csv('News_Crawling/ES/[엔씨소프트] price_labeling.csv')
        
        # print('News data info')
        # print(self.news.info())

        # emotion dict
        self.word_list = []
        self.total_word_df=pd.DataFrame(columns={"word","count"})
    
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
                    input parameter : None
                    output : word & freq dictionary(csv file)
                            (frequency가 100미만인 단어는 제외, frequency 내림차순 정렬)
        '''

        # news data column 설정
        self.set_columns()

        # content 중 기업명 제외하기 - apply 함수 사용
        self.news['Content'] = self.news['Content'].apply(self.remove_keyword)
        
        ### [version. soynlp] ###
        # 명사 추출기
        noun_extractor = NewsNounExtractor(
            max_left_length=10, 
            max_right_length=7,
            predictor_fnames=None,
            verbose=True
            )   
        
        nouns = noun_extractor.train_extract(
            self.news['Content'][0]
            )

        top500 = sorted(nouns.items(),
            key=lambda x:-x[1].frequency)[:500]
        
        for i, (word, score) in enumerate(top500):
            if i % 5 == 0:
                print()
            print('%6s (%.2f)' % (word, score.score), end='')



        ### [version 1] ###
        # 동사, 형용사, 명사만을 words에 추가
        # self.news['Word'] = self.news['Content'].apply(self.build_word)


        ### [version 2] ###
        # 1. 동사, 형용사, 명사만을 words에 추가
        # 2. [불용어 처리] 1) LEN 1 제외
        # mecab  = Mecab()
        # for idx in range(len(self.news['Content'])):
        #     mecab_tag = mecab.pos(self.news['Content'][idx])
        #     for tagg in mecab_tag:
        #         if (tagg[1][0] == 'N' or tagg[1][0] == 'V') and (len(tagg[0]) != 1):
        #             self.word_list.append(tagg[0])
        

        # 불용어 처리
        '''
            불용어 처리
                이미 해본 방식 :: 1) LEN 1 제외, 2) 한글 불용어 100에 있는 단어 제외
                1) LEN 1 제외 -- 완료
                2) 한글 불용어 100 파일이 어디에 있는거야 !!?
        '''

        # 각 단어의 빈도수를 내림차순으로 저장
        # self.count_items = Counter(self.word_list)
        # self.word_freq = self.count_items.most_common()

        # self.top_500 = self.count_items.most_common(n=500)
        # print('\n Top 500 frequency words')
        # print(self.top_500)
        # print('\n')

        # 튜플 형태를 딕셔너리로 바꾸기
        # self.word_freq_dict = dict((x, y) for x,y in self.word_freq if y>=100)
        # print(self.word_freq_dict)
        

        # 유니크한 단어가 몇개 나오는지 출력
        # print("\nThe number of Unique words :", len(np.unique(self.word_freq)))
        # print('\n')


        # 단어 csv로 저장
        # for key,value in (self.word_freq_dict.items()):
        #     data={"word":key,"count":value}  
        #     self.total_word_df=self.total_word_df.append(data,ignore_index=True)
        
        # self.total_word_df=self.total_word_df[["word","count"]]
        # self.dataframe = pd.DataFrame(self.total_word_df)
        # self.dataframe.to_csv("[엔씨소프트]word_dictionary_sonlpy.csv",header=True,index=False)


if __name__ == "__main__":
    '''
    Crawling class 실행
    '''

    # crawling class 선언
    EA = preprocessing_soynlp()
    
    # 형태소 분석
    EA.content_tag()