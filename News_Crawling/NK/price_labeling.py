import pandas as pd
import requests


class Price:

    ## [업데이트 예정] 시세 데이터 라벨링 함수 ##
    def stock_price_labeling(self, stock_price):

        '''
        stock_price_labeling() : 시세 데이터 라벨링 함수 
            input parameter : (Dataframe) stock_price
            
            output : 라벨링 데이터 csv 파일로 저장 
        ''' 

        # 0으로 초기화 된 label 칼럼 추가 
        stock_price['label'] = 0
        # int 형으로 전환 
        stock_price = stock_price.astype({'close':'int'})
        stock_price = stock_price.reset_index(drop = True)

        # 전일비 값을 구하여 라벨링 
        for i in range(1,len(stock_price['close'])-1):    
            diff = (stock_price['close'][i] - stock_price['close'][i+1])
            if (diff > 0) : stock_price['label'][i] = 1
            elif diff == 0 : stock_price['label'][i] = 0
            else : stock_price['label'][i] = -1

        #csv 파일로 저장 
        stock_price.to_csv(f"C:/Users/82102/OneDrive/문서/Emotion-Recognization/News_Crawling/NK/price_labeling.csv",header=False,index=False) 
        
    ## 한 종목의 시세 데이터 크롤링 함수 ##
    def stock_price_crawling(self):

        '''
        stock_price_crawling() : 한 종목의 시세 데이터 크롤링 함수 
            input parameter : (str) code, (str) company
                시세 데이터 라벨링을 위한 stock_price_labeling 함수 호출 
            output : 시세 라벨링 csv 파일 저장
        '''

        stock_price = pd.DataFrame()
        
        stock_price = pd.read_csv('C:/Users/82102/OneDrive/문서/Emotion-Recognization/News_Crawling/NK/price_crawling.csv')

        stock_price = stock_price.dropna()
        
        stock_price = stock_price[['date', 'close']]   

        stock_price['date'] = stock_price['date'].replace('.','-')             
        # 칼럼 순서 재조합                                                                               
        stock_price = stock_price[['date','close']]   

        # 시세 데이터 라벨링 함수 호출 
        self.stock_price_labeling(stock_price)                                                               


if __name__ == '__main__':
    price = Price()
    price.stock_price_crawling()
