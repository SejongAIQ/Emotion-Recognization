import pandas as pd                             # For Data Management
import matplotlib.pyplot as plt                 # For Data Visualization
from konlpy.tag import Kkma                     # For Natural Language Processing
from nltk import word_tokenize, sent_tokenize      
from collections import Counter                 # For nouns counting 

#nltk.download()


class Sentiment_Lexicon:
    def __init__(self):
    
        # 형태소 분석기 선언 
        self.kkma = Kkma()

        # [ 구축 예정 ] 불용어 사전 로드
        stopwords = pd.read_csv("https://raw.githubusercontent.com/yoonkt200/FastCampusDataset/master/korean_stopwords.txt").values.tolist()
        self.stop_words = set(x[0] for x in stopwords)

    def combining_news(self,News):

        '''
        combining_strings() : 개별 뉴스 데이터 취합 함수  
            input parameter : (dataframe) News
            output : (String) combinated_news        
        '''
        
        # 개별 뉴스 데이터 취합 
        combinated_news = ""
        for i in range(0,len(News)):
            combinated_news = combinated_news + " " + News['content'][i]

        return combinated_news

    def stopwords_deletion(self, word_tokens):
        
        '''
        stopwords_deletion() :  stop word 제거 함수 
            input parameter : (list) word_tokens
            output :  stop word 제거 완료
        '''

        filtered_words = []

        # 토큰화된 개별 단어가 스톱 워드의 단어에 포함되지 않으면 word_tokens에 추가 
        if tuple(word_tokens) not in self.stop_words:
            filtered_words.append(word_tokens)

        print("stop word filtering is done.")

    def count_word(self, words):
        
        '''
        count_word() : 명사 빈도 카운팅 함수 
            input parameter : (list) word_list
            output : 명사 빈도 출력 및 시각화 
        '''

        # 단어 빈도 카운트 
        count = Counter(words)
        # [ 출력 기준 필요 ] 최빈값 명사 100개 반환 
        word_list = count.most_common(100)
        # 최빈값 명사 100개 출력 
        for word in word_list:
            print(word)

    def konlpy_test(self, combinated_news):

        '''
        konlpy_test() : konlpy 툴 테스트 함수 
            input parameter : (String) combinated_news
                stop word를 제거하기 위해 stopwords_deletion 함수 실행 
                명사 빈도를 카운팅하기 위해 count_word 함수 실행 
            output : 최빈값 명사 출력
        '''

        print(combinated_news)
        # 명사 추출 
        nouns = self.kkma.nouns(combinated_news)
        # 한 글자 명사 제거 
        for i,v in enumerate(nouns):
            if len(v)<2:
                nouns.pop(i)
        print("extract nouns is done")

        # stop word 제거 
        #filtered_nouns = self.stopwords_deletion(nouns) 

        # 명사 빈도 카운트 
        self.count_word(nouns)       
    
    def nltk_test(self, combinated_news):
        
        '''
        nltk_test() : nltk_test 툴 테스트 함수 
            input parameter : (String) combinated_news
            output : 최빈값 명사 출력 
        '''

        # 문장별로 단어 토큰화 
        sentences = sent_tokenize(combinated_news)
        # 분리된 문장별 단어 토큰화 
        word_tokens = [ word_tokenize(sentences) for sentence in sentences ]
        print(word_tokens)

        # stop word 제거 
        filtered_words = self.stopwords_deletion(word_tokens) 

        # 단어 빈도 카운트 
        self.count_word(filtered_words)
    
    def extract_nouns(self, code, company):

        '''
        extract_nouns() : 형태소 분석을 통해 명사 추출 함수
            input parameter :
                개별 데이터를 합치기 위해 combining_news() 호출
            output : 추출된 명사 리스트 반환  
        '''

        # 해당 기업의 뉴스 데이터 로드 
        News = pd.read_csv(f'C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/DATA/News/[{company}]news_data.csv', names = ['date','title','content'])
        # 해당 기업의 뉴스 데이터 취합 
        combinated_news = sentiment_lexicon.combining_news(News)

        ### [ 1. konlpy 사용 ] ###
        self.konlpy_test(combinated_news)

        ### [ 2. nltk 사용 ] ###
        self.nltk_test(combinated_news)
        
    def load_data_by_sector(self):

        '''
        load_data_by_sector() : 섹터별 데이터 로드 함수 
            input parameter :
                한 종목의 명사 추출을 위한 extract_nouns 함수 호출 
            output : 전 종목의 명사 추출 완료
        '''
        
        # 업종별 코드 로드
        codes_list = pd.read_csv('C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/code_by_Sector.csv', encoding = 'cp949')

        # NaN 데이터 삭제                          
        codes_list = codes_list.dropna()
        # 전체 데이터 string으로 형 변환                    
        codes_list = codes_list.applymap(str) 

        # 종목별 뉴스 데이터 명사 추출 실행 
        for i in range(len(codes_list)):
            print(f"[{codes_list['code'][i]}] Start to Extract nouns ... " )
            # code 자리수 6개로 고정 
            sentiment_lexicon.extract_nouns(codes_list['code'][i].zfill(6),codes_list['company'][i])
            

if __name__ == "__main__":
    sentiment_lexicon = Sentiment_Lexicon()
    sentiment_lexicon.load_data_by_sector()