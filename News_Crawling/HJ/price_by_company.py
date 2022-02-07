from isort import code
import pandas as pd
import requests


class Price:

    ## [업데이트 예정] 시세 데이터 라벨링 함수 ##
    def stock_price_labeling(self, company, stock_price):

        '''
        stock_price_labeling() : 시세 데이터 라벨링 함수 
            input parameter : (str) company, (Dataframe) stock_price
            
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
        stock_price.to_csv(f"C:/Users/user/OneDrive/바탕 화면/AI_QUANT/[{company}] price_labeling.csv",header=False,index=False) 
        
    ## 한 종목의 시세 데이터 크롤링 함수 ##
    def stock_price_crawling(self, code, company):

        '''
        stock_price_crawling() : 한 종목의 시세 데이터 크롤링 함수 
            input parameter : (str) code, (str) company
                시세 데이터 라벨링을 위한 stock_price_labeling 함수 호출 
            output : 시세 라벨링 csv 파일 저장
        '''

        stock_price = pd.DataFrame()
        lastpage = 26

        # 네이버 금융 사이트 불러오기 
        url = f"http://finance.naver.com/item/sise_day.nhn?code={code}"         
        # page_url의 html 파일                                                       
        for page in range(1, lastpage + 1):                                     
            pg_url = f'{url}&page={page}'                               
            stock_price = stock_price.append(pd.read_html(requests.get(pg_url, headers = {'User-agent' : 'Mozilla/5.0'}).text)[0])                   

            # 다운로드 현황 출력 
            print('[stock_price]::({}) {:04d}/{:04d} pages are downloading...'.format(company, page, lastpage))      

        stock_price = stock_price.dropna()
        # 날짜와 종가 데이터만 추출
        stock_price = stock_price[['날짜', '종가']]   
        # 칼럼명 영문으로 변환                                                                                          
        stock_price = stock_price.rename(columns={'날짜':'date','종가':'close'})
        stock_price['date'] = stock_price['date'].replace('.','-')             
        # 칼럼 순서 재조합                                                                               
        stock_price = stock_price[['date','close']]   

        # 시세 데이터 라벨링 함수 호출 
        self.stock_price_labeling(company,stock_price)                                                               

    ## 섹터별 데이터 로드 함수 ## 
    def load_price_by_sector(self):   

        '''
        news_content_crawling() : 섹터별 데이터 로드 함수  
            input parameter :
                한 종목의 시세 데이터 크롤링을 위한 stock_price_crawling 함수 호출
                한 종목의 시세 데이터 라벨링을 위한 stock_price_labeling 함수 호출 
            output : 전 종목 시세 데이터 크롤링 및 라벨링 완료
        '''

        # 업종별 코드 로드 
        codes_list = pd.read_csv('C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/code_by_Sector.csv', encoding = 'cp949')     

        # NaN 데이터 삭제                          
        codes_list = codes_list.dropna()
        # 전체 데이터 string으로 형 변환                    
        codes_list = codes_list.applymap(str)          

        # 종목별 시세 데이터 크롤링 및 라벨링 함수 실행 
        for i in range(len(codes_list)):
            print(f"[{codes_list['code'][i]}] Start price data Crawling" )
            # code 자리수 6개로 고정 
            price.stock_price_crawling(codes_list['code'][i].zfill(6),codes_list['company'][i])  

if __name__ == '__main__':
    price = Price()
    price.load_price_by_sector()