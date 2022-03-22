from contextlib import closing
import pandas as pd                             # For Data Management
import numpy as np                              # 
import re                                       # For Text Processing
from eunjeon import Mecab                       # For Natural Language Processing    
from collections import Counter
from pymysql import NULL

from sklearn import preprocessing                 # For nouns counting 

class Sentiment_Lexicon:
    def __init__(self):
    
        # 형태소 분석기 선언 
        self.mecab = Mecab()

        # [ 임시 ] 불용어 
        self.stopwords = ['기업', '금융', '언론사', '경제', '사업', '우편','종목','뉴스','지수']
        # [ 구축 예정 ] 불용어 사전 로드
        # stopwords = pd.read_csv("https://raw.githubusercontent.com/yoonkt200/FastCampusDataset/master/korean_stopwords.txt").values.tolist()
        # self.stop_words = set(x[0] for x in stopwords)

    ## 개별 데이터 취합 함수 ##
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

        print("combination is done.")
        return combinated_news

    ## 불용어 제거 함수 ##
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
    
    ## 텍스트 전처리 함수 ##
    def preprocessing(self, company, text, idx, process_code):

        '''
        preprocessing() : 텍스트 전처리 함수
            input parameter : (String) text
                (1) 특수문자 제거
                (2) 기업명 제거 
                (3) NaN 데이터 처리 
            output : 제거된 데이터 반환 
        '''

        if process_code == 'News':
            # 특수문자 제거 
            text = re.sub('[^가-힣a-z]', ' ', text)
            # 기업명 제거 :: ex) 회사(은/는/이/가) | 회사(을/를) | 회사(다/이다) ?
            processed_text = re.sub(f'[{company}]','', text)
            
            return processed_text

        #print("------remove is done.------")
        #print(combinated_news)
  
        elif process_code == 'NaN':
            # NaN label 데이터 처리 
            for i in range(idx, len(text)):
                if np.isnan(text[i]) == 0 :
                    return text[i]

    ## 단어 추출 함수 ##
    def extract_nouns(self, code, company):

        '''
        extract_nouns() : 형태소 분석을 통해 명사 추출 함수
            input parameter :
                개별 데이터를 합치기 위해 combining_news() 호출
            output : 추출된 명사 리스트 반환  
        '''

        # 단어 저장 리스트 
        words = list()
        # 단어 사전 DF 
        lexicon = pd.DataFrame(columns=['morph','count'])

        # 해당 기업의 뉴스 데이터 로드  
        News = pd.read_csv(f'C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/DATA/News/[{company}]news_data.csv', names = ['date','title','content'])
        # 해당 기업의 뉴스 데이터 취합 
        combinated_news = sentiment_lexicon.combining_news(News)
        # 텍스트 전처리 함수 [특수문자, 기업명 제거]
        processed_text = self.preprocessing(company, combinated_news, 0, 'News')

        # 형태소 추출 
        for token in self.mecab.pos(processed_text):
            # 일반 명사, 고유 명사, 대명사, 동사, 형용사이면서 길이가 1이 아닌 경우,
            # 불용어 제거 후, 리스트에 저장   
            if token[1] in ['NNG', 'NNP', 'NP', 'VV','VA'] and token[0] not in self.stopwords and len(token[0]) > 1:
                words.append(token[0])

        print(f'[{company}] list len :: {len(words)}')

        # 빈도수 카운팅
        morph_list = Counter(words).most_common()
        #for m in morph_list:
        #    print(m)

        # 리스트를 df 형태로 변형 
        morph_df = pd.DataFrame(morph_list, columns = ['dict','count'])
        # 상위 25% 기준선 추출 
        count_75 = (morph_df['count'].describe())['75%']
        # 상위 25% 이하의 데이터 삭제 
        drop_idx = morph_df[morph_df['count'] < count_75].index
        lexicon = morph_df.drop(drop_idx)

        print(lexicon)

        # 최종 데이터 column 순서 정리 후, csv 파일로 저장 
        lexicon = lexicon[["dict","count"]]                          
        lexicon.to_csv(f"C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/DATA/lexicon/[{company}] lexicon_test.csv",header=False,index=False)

        print(f"[{company}] extraction is done.")

    ## 휴장일과 시세 데이터 병합 함수 ##
    def merge_closing_date_with_price(self, company):

        '''
        merge_closing_date_with_price() : 휴장일과 시세 데이터 병합 함수 
            input parameter : (String) code 
                ( 0: 시세 변동 없음, 1: 상승, -1: 하락, 999: 휴장 )
            output : 휴장일과 시세 데이터 병합 완료 
        '''

        # 각 데이터 로드 
        closing_day = pd.read_csv('C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/DATA/closing_day_ver2.csv',encoding='cp949')
        closing_day = closing_day.rename(columns={'날짜':'date','요일':'day','휴일':'closing'})

        price_labeling = pd.read_csv(f'C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/DATA/Price/[{company}] price_labeling.csv', names = ['date','price','label'])

        # 날짜에 맞춰 데이터 병합 
        merge_data = pd.merge(closing_day,price_labeling,how='outer')
        merge_data.drop(columns=['day','price'],axis=1,inplace=True)

        # NaN 값 보완 
        # NaN :: 이후 가까운 라벨 값으로 대체 
        # EX ) 토,일 -> 월 
        for idx in range(len(merge_data)):
            if np.isnan(merge_data['label'][idx]) :
                merge_data['label'][idx] = self.preprocessing(company, merge_data['label'], idx, 'NaN')

        # 최종 데이터 column 순서 정리 후, csv 파일로 저장
        merge_data = merge_data[['date','label','closing']]
        merge_data['label'] = merge_data['label'].astype(int)
        merge_data.to_csv(f"C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/DATA/lexicon/final_label/[{company}] final_label.csv",header=True,index=False)

        print(f"[{company}]'s final_label is saved. ")

    ## 섹터별 데이터 로드 함수 ##
    def load_data_by_sector(self):

        '''
        load_data_by_sector() : 섹터별 데이터 로드 함수 
            input parameter :
                한 종목의 명사 추출을 위한 extract_nouns 함수 호출 
                한 종목의 시세 데이터와 휴장일 병합을 위한 merge_closing_date_with_price 함수 호출 
            output : 전 종목의 명사 추출 완료
        '''
        
        # 업종별 코드 로드
        codes_list = pd.read_csv('C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/code_by_Sector.csv', encoding = 'cp949')

        # NaN 데이터 삭제                          
        codes_list = codes_list.dropna()
        # 전체 데이터 string으로 형 변환                    
        codes_list = codes_list.applymap(str) 

        # 종목별 뉴스 데이터 명사 추출 및 시세 데이터 병합 실행 
        for i in range(len(codes_list)):
            print(f"[{codes_list['code'][i]}] Start to Extract nouns ... " )
            # code 자리수 6개로 고정 
            # sentiment_lexicon.extract_nouns(codes_list['code'][i].zfill(6),codes_list['company'][i])
            # 해당 종목의 시세 데이터와 휴장일 병합 
            sentiment_lexicon.merge_closing_date_with_price(codes_list['company'][i])
            
            

if __name__ == "__main__":
    sentiment_lexicon = Sentiment_Lexicon()
    sentiment_lexicon.load_data_by_sector()