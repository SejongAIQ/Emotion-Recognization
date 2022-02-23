from konlpy.tag import Kkma
from eunjeon import Mecab
from collections import Counter
import pandas as pd
import re
import urllib3
urllib3.disable_warnings()

class emotion:
    def __init__(self):
        '''
        __init__() : 초기화 함수
                    mecab 형태소 분석기 선언
        '''
        self.mecab=Mecab()

    def clean_text(self, text):
        '''
        clean_text() : 텍스트 전처리 함수
                            불용어 지정, 형태소 분석 
        '''

        txt = re.sub('[^가-힣a-z]', ' ', text)
        txt = re.sub('기자', ' ', text)
        token = self.mecab.pos(txt)
        
        stopwords = pd.read_csv("https://raw.githubusercontent.com/yoonkt200/FastCampusDataset/master/korean_stopwords.txt").values.tolist()
        stop_words = set(x[0] for x in stopwords)
        token = [t for t in token if t not in stop_words]
        return token

    def text_preprocessing(self):
        '''
        text_preprocessing() :  사전 만드는 함수
        '''
        #데이터 로드
        news_data = pd.read_csv("C:/Users/82102/OneDrive/문서/Nakyung-Emotion-Recognization/News_Crawling/NK/news_crawling.csv")

        df=pd.DataFrame(columns={"word","count"})
        news=[]

        for i in range(len(news_data)):
            #텍스트 데이터 전처리
            str=self.clean_text(news_data['title'][i]+news_data['content'][i])
            for j in range(len(str)):
                if str[j][1].startswith('N') or str[j][1].startswith('V'): 
                    #키워드로 보기 힘든 한글자 형태소 제거
                    if len(str[j][0])>2:
                        news.append(str[j][0])

        #추출한 형태소 카운트
        count = Counter(news)
        
        cnt=len(count)//4

        # 빈도가 높은 단어만 추출
        data_list = count.most_common(cnt)

        #튜플 -> 딕셔너리
        data_li=dict((x,y)for x,y in data_list)

        for key,value in (data_li.items()):
            data={"word":key,"count":value}  
            df=df.append(data,ignore_index=True)

        df=df[["word","count"]]
        dataframe = pd.DataFrame(df)
        dataframe.to_csv("C:/Users/82102/OneDrive/문서/Nakyung-Emotion-Recognization/News_Crawling/NK/news_data_analysis.csv",header=True,index=False)

      
if __name__ == "__main__":
    Emotion = emotion()
    Emotion.text_preprocessing()

