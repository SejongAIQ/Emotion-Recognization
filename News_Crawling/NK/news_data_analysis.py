from konlpy.tag import Kkma
from collections import Counter
import pandas as pd
import re

news_data = pd.read_csv('news_crawling.csv')
kkma=Kkma()
def text_preprocessing(text):
    '''
    text_processing() : 텍스트 전처리 함수
                        불용어 지정, 형태소 분석 
    '''
    stopwords = ['을', '를', '에','의','으로','로','에게','이','있','그', '가', '은', '는','나','와','과','가','기자']
    txt = re.sub('[^가-힣a-z]', ' ', text)
    token = kkma.nouns(txt)
    token = [t for t in token if t not in stopwords]
    return token

df=pd.DataFrame(columns={"word","count"})
news=[]

for i in range(len(news_data)):
    #텍스트 데이터 전처리
    str=text_preprocessing(news_data['content'][i])
    for j in range(len(str)):
        news.append(str[j])

#키워드로 보기 힘든 한글자 형태소 제거
for i,v in enumerate(news):
    if len(v)<2:
        news.pop(i)

#추출한 형태소 카운트
count = Counter(news)

#약 8800개 이상의 결과 / 빈도가 높은 2000개만 추출
data_list = count.most_common(2000)

#튜플 -> 딕셔너리
data_li=dict((x,y)for x,y in data_list)

for key,value in (data_li.items()):
    data={"word":key,"count":value}  
    df=df.append(data,ignore_index=True)
        
df=df[["word","count"]]
dataframe = pd.DataFrame(df)
dataframe.to_csv("news_data_analysis.csv",header=True,index=False)

