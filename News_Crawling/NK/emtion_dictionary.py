import pandas as pd
from datetime import datetime

class Dic:
    def __init__(self):
        '''
        __init__() : 초기화 함수
                    필요한 csv 파일 불러오기
        '''

        self.words = pd.read_csv("news_data_analysis.csv")
        self.news_data = pd.read_csv("news_crawling.csv")
        self.price = pd.read_csv("price_crawling.csv")

    def include(self,i,j):
        '''
            include() : 포함여부 확인 함수
                        기사 j 에 단어 i 가 포함되어 있으면 1 아니면 0
        '''

        if self.words['word'][i] in self.news_data['content'][j]:
            return 1
        else:
            return 0

    def NSP(self,j):
        '''
            NSP() : 익일 주가 상승 여부 확인 함수
                    기사 j 에 단어 i 가 포함되어 있으면 1 아니면 0
        '''

        nsp=[]
        i=len(self.price)-1

        date=self.news_data['date'][j][:11]
        mo=date[6:8]
        day=date[9:11]

        time1=datetime(2021,int(mo),int(day))
        time2=datetime(2021,int(self.price['date'][i][5:7]),int(self.price['date'][i][8:10]))
        
        while True:
            time2=datetime(2021,int(self.price['date'][i][5:7]),int(self.price['date'][i][8:10]))
            if (time1-time2).days > 0:
                i-=1
            else:
                break

        try:
            #주가 상승 여부 (익일 주가)
            if self.price['diff'][i-1]>0:
                nsp=1
            else:
                nsp=0
        except:
            nsp=0

        return nsp

    def dic(self):
        '''
            dic() : 긍정지수 딕셔너리 생성 함수
                    기사 j 에 단어 i 가 포함되어 있고 X 기사 j 게재 후 주가 상승하면 -> 1
        '''
        
        P={} 
        df=pd.DataFrame(columns={"word","positive_index"})

        for i in range(len(self.words)):
            I=[] #include
            N=[] #NSP
            S=[] #I X N

            for j in range(len(self.news_data)-1,0,-1):
                I.append(self.include(i,j))
                N.append(self.NSP(j))

            for f,p in zip(I, N):
                S.append(f*p)

            try:
                data={"word":self.words['word'][i],"positive_index":(sum(S)/sum(I))}  
                df=df.append(data,ignore_index=True)
            except:
                data={"word":self.words['word'][i],"positive_index":0}  
                df=df.append(data,ignore_index=True)
        
        df=df[["word","positive_index"]]
        print(df)
        dataframe = pd.DataFrame(df)
        dataframe.to_csv("emotion_dictionary.csv",header=True,index=False)


if __name__ == "__main__":
    Dictionary=Dic()
    Dictionary.dic()