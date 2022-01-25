import code
from typing import Counter
import pymysql                                  #DB 관리 라이브러리 
import requests    
import pandas as pd                             
from datetime import datetime, timedelta        # 날짜/시간 라이브러리
from bs4 import BeautifulSoup              # html 파일 관리 라이브러리

import urllib3
urllib3.disable_warnings()

class News:
 
    def __init__(self): #초기화 함수
        self.conn = pymysql.connect(host='localhost', user='root', password = '1234', db = 'NEWS', charset='utf8')
    def __del__(self):  #소멸자 함수        
        self.conn.close()                       # DB 연결 해제 
    
    ## [업데이트 예정] 시세 데이터 라벨링 함수 ##
    def sise_labeling(self): 
        sise = pd.read_csv('sise_data.csv')
    ## 시세 데이터 크롤링 함수 ##
    def stock_price_crawling(self):
        
        df = pd.DataFrame() 
        code = news.stock_code()
        lastpage = 26

        url = f"http://finance.naver.com/item/sise_day.nhn?code={code}"         #네이버 금융 사이트 불러오기 
                                                              
        for page in range(1, lastpage + 1):                                     #페이지 수 만큼 반복
            pg_url = '{}&page={}'.format(url, page)                             #page별 url따기 -> format : 대괄호에 들어갈 값을 연결     
            df = df.append(pd.read_html(requests.get(pg_url, headers = {'User-agent' : 'Mozilla/5.0'}).text)[0])                    #각 page를 html파일을 df에 저장
            
            print('[stock_price]::({}) {:04d}/{:04d} pages are downloading...'.format(code, page, lastpage))      #현재 시간에 어디까지 다운로드 했는지 저장
                                                                                                    
        df = df.rename(columns={'날짜':'date','종가':'close','전일비':'diff','시가':'open','고가':'high','저가':'low','거래량':'volume'})   #각 칼럼의 이름을 영문으로 바꿈
        df['date'] = df['date'].replace('.','-')                                                                                          #데이터의 '.'를 '-'로 바꿈
        df = df.dropna()                                                                                                                  #dropna : 결측값 제거, dropna() : 결측값 있는 전체 행 삭제 
        df = df[['date','open','high','low','close','diff','volume']]                                                                     #원하는 순서대로 칼럼 재조합   
           
        #csv 파일로 저장 
        dataframe = pd.DataFrame(df)
        dataframe.to_csv("C:/Users/user/OneDrive/바탕 화면/AI_QUANT/[F&F]stock_price.csv",header=False,index=False)

    ## 데이터 정제 함수 ##
    def title_clean(self,text):     
        cleaned_text = text.replace('···',"")
        cleaned_text = cleaned_text.replace('…',"")
        cleaned_text = cleaned_text.replace('.',"")
        ### 추가 예정 ###
        return cleaned_text
    def content_clean(self,text):
        cleaned_text = text.replace('\n',"")
        cleaned_text = cleaned_text.replace('\t',"")
        cleaned_text = cleaned_text.replace('···',"")
        cleaned_text = cleaned_text.replace('…',"")
        cleaned_text = cleaned_text.replace('.',"")
        cleaned_text = cleaned_text.replace(',',"")
        ### 추가 예정 ###
        return cleaned_text    
    def cleaning(self,raw_data):  
        cleaned_title = news.title_clean(raw_data['title'])
        cleaned_content = news.content_clean(raw_data['content'])
  
        raw_data['title'] = cleaned_title
        raw_data['content'] = cleaned_content

        return raw_data

    ## 한 종목의 뉴스 last_url 반환 함수 ##
    def find_last_url(self, url):

        while True:
            # 맨뒤 페이지 html 가져오기 
            url_html = BeautifulSoup(requests.get(url, verify=False, headers = {'User-agent' : 'Mozilla/5.0'}).text,"lxml")
            
            # pgRR 태그가 존재하는 경우
            if url_html.select('td.pgRR > a'): # pgRR 태그가 존재하는 경우 
                href = url_html.select('td.pgRR > a')[0]['href']
                url = f"https://finance.naver.com{href}"           

            # on 태그가 존재하는 경우 ( 맨 마지막 페이지 )
            else: 
                href = url_html.select('td.on > a')[0]['href']
                last_url = f"https://finance.naver.com{href}" 
                return last_url           
    ## 한 종목의 뉴스 url list 반환 함수 ##
    def read_naver_news(self,code):  

        page =  1                               # 초기 페이지 
        url_list = []                           # 각 뉴스의 url list

        try:
            while True:
                # 네이버 금융 글로벌 경제 url 
                url=f"https://finance.naver.com/item/news_news.naver?code={code}&page={page}&sm=entity_id.basic&clusterId="
                html_news = BeautifulSoup(requests.get(url, verify=False, headers = {'User-agent' : 'Mozilla/5.0'}).text,"lxml")

                #lastpage url 로드
                if page == 1: 
                    href = html_news.select('td.pgRR > a')[0]['href']
                    pgRR_url = f"https://finance.naver.com{href}" 
                    last_url = news.find_last_url(pgRR_url)
                    
                #a 태그 로드 
                a_tag_list = html_news.select('table.type5 > tbody > tr > td > a')     
               
                for i in range(len(a_tag_list)):                        # url 원소 1개씩 list에 저장 
                    news_url = a_tag_list[i]['href']                   
                    url_list.append(news_url)

                if last_url == url:                                     # 종료 조건 :: last_url과 url 같을 경우 종료 
                    return url_list 
                    
                page = page + 1                                               # 데이터 업데이트
 
        except Exception as e:                                          # 에러 발생 시, 에러 출력 
            print('Exception occured :', str(e))
            return None
    ## 한 종목의 뉴스 데이터 크롤링 함수 ##
    def news_content_crawling(self,code,company):  
        
        df = pd.DataFrame(columns={"date","title","content"})           # df 생성 [ 종목별 뉴스 데이터 저장 ] 
        url_list = news.read_naver_news(code)                           # url_list 로드
                                            
        for i in range(len(url_list)):                                  
            
            url=f"https://finance.naver.com{url_list[i]}"                   # 1개의 url 가져오기 
            html_news = BeautifulSoup(requests.get(url, verify=False, headers = {'User-agent' : 'Mozilla/5.0'}).text,"lxml")  # parser

            time = html_news.find("span",class_ = "tah p11").get_text()     # time 긁어오기
            title = html_news.find("strong",class_ = 'c p15').get_text()    # title 긁어오기
            content = html_news.find("div",class_ = "scr01").get_text()     # 뉴스 본문 긁어오기  
            
            data_list = {"date":time, "title":title, "content":content}     # series 형식으로 데이터 저장

            data_list = news.cleaning(data_list)                            # 데이터 정제 
            df = df.append(data_list, ignore_index=True)                    # 데이터 프레임에 추가 

            print('[news_data]::({}) {}/{} pages are downloading...'.format(company,i+1,len(url_list))) # 다운로드 현황 출력
        
        df = df[["date","title","content"]]                             # column 순서 맞추기

        #csv 파일로 저장 
        dataframe = pd.DataFrame(df)
        dataframe.to_csv(f"C:/Users/user/OneDrive/바탕 화면/AI_QUANT/DATA/[{company}]news_data.csv",header=False,index=False)

    ## 섹터별 데이터 로드 함수 ## 
    def load_news_by_sector(self):   
        
        codes_list = pd.read_csv('./DATA/code_by_Sector.csv', encoding = 'cp949')                                      # 업종 코드 로드
        
        codes_list = codes_list.dropna()                    # NaN 데이터 삭제 
        codes_list = codes_list.applymap(str)               # 문자열로 형 변환 

        for i in range(len(codes_list)):
            codes_list['code'][i] = codes_list['code'][i].zfill(6)    # 6자리로 고정
            print(f"[{codes_list['code'][i]}] Start news data Crawling" )
            news.news_content_crawling(codes_list['code'][i].zfill(6),codes_list['company'][i])      # 업종 코드 별, 뉴스 데이터 크롤링 


if __name__ == "__main__":
    news = News()
    #news.example()
    news.load_news_by_sector()
    #news.stock_price_crawling()





