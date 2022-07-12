""" 주식종목 뉴스(네이버 파이넌스) Crawling 하기 """  
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os 
from newspaper import Article
import pymysql, json, calendar

import urllib3
urllib3.disable_warnings()
class DBUpdater:
    def __init__(self):     #초기화 함수 - self 자기 자신을 의미함 
        """생성자: DB 연결 및 종목코드 딕셔너리 생성"""
        self.conn = pymysql.connect(host="localhost", user='root', password = ' ', db = 'ai_quant', charset ='utf8' ) #db 연결 

        with self.conn.cursor() as curs:            #self.conn.cursor을 불러와서 curs로 사용한다. cursor : sql문을 실행하기 위해 필요함 
            sql="""
            CREATE TABLE IF NOT EXISTS news_raw (
                date VARCHAR(100),
                title VARCHAR(100),
                content LONGTEXT )
            """                                   #sql문 작성 
            curs.execute(sql)                       #sql문 전달 및 실행 
            
        self.conn.commit()                      #DB 최종 저장 
    
    def __del__(self):
        """소멸자: DB 연결 해제 """
        self.conn.close()

    def replace_into_db(self, df):                              
        """네이버에서 읽어온 뉴스 기사 DB에 REPLACE"""
        count = 1
        with self.conn.cursor() as curs:                                            #cursor(db접근 시, 필요) 불러오기 
            for r in df.itertuples():                                               #itertuples(): 튜플 형식으로 한 줄씩 불러옴
                sql = f"REPLACE INTO news_raw VALUES ('{r.date}','{r.title}','{r.content}')" #값을 바꾼다는 sql 문
                curs.execute(sql)                                                   #sql문 실행

                print('{}/{} pages are downloading...'.format(count,len(df))) # 다운로드 현황 출력
                count += 1   

            self.conn.commit()  
          

    def find_url(self,company_code):
        '''
        find_url() 함수: 모든 기사 링크를 찾아 link_result 배열에 저장하는 함수
                input parameter : (str)company_code
                output : (list)link_result
        '''
        
        page=1
        link_result=[]
        #마지막 페이지
        #last_page=find_lastpage("news",company_code)  
        last_page = 1
        while True:
            if page==int(last_page)+1: break      
            url=f"https://finance.naver.com/item/news_news.naver?code={company_code}&page={page}&sm=title_entity_id.basic&clusterId="
            html=BeautifulSoup(requests.get(url,verify=False,headers={'User-agent' : 'Mozilla/5.0'}).text, 'html.parser')
            # 뉴스 링크
            links = html.select('.title')    
            for link in links: 
                add = 'https://finance.naver.com' + link.find('a')['href']
                link_result.append(add)
            page+=1
            
        return link_result

    def cleaning_text(self,df):
        '''
        cleaning_text() 함수: 특수문자 공백 반복적인 마침표 제거
                input parameter : (str)df
                output : (str)df
        '''
        
        while ('.' in df):
            df = df.replace('.', '')
        df = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\◆(\)\[\]\<\>`\'…》]',' ', df)
        df = re.sub('대한항공',' ', df)
        df = ' '.join(df.split()).rstrip()
        
        return df

    def find_text(self,company_code):
        '''
        find_text() 함수: 뉴스.공시 데이터 크롤링
                input parameter : (str)company_code
                output : (DataFrame)dataframe
        '''
    
        df=pd.DataFrame(columns={"date","title","content"})
        link_result=self.find_url(company_code)
        
        for i in range(len(link_result)):
            url=link_result[i]
            html_news=BeautifulSoup(requests.get(url,verify=False,headers={'User-agent' : 'Mozilla/5.0'}).text, 'html.parser')
            '''
            html_news / time / title / content
            '''      
            
            time=html_news.find("span",{"class": "tah p11"}).get_text()
            title=html_news.find("strong",{"class": "c p15"}).get_text()   
            content=html_news.find(id="news_read").get_text()
            
            #link_news 태그의 내용이 함께 출력됨 -> 해당 태그 내용 remove 진행
            if html_news.find("div",class_="link_news") != None:
                remove=html_news.find("div",class_="link_news").get_text()
                content=content.replace(remove,"")
                #데이터 전처리 진행
                title = self.cleaning_text(title)
                title = ' '.join(title.split())
                content = self.cleaning_text(content)
                content = ' '.join(content.split())    
            
            
            #data_list
            data_list={"date":time,"title":title,"content":content}   
            df=df.append(data_list,ignore_index=True)
            
        
        df=df[["date","title","content"]]   

        dataframe=pd.DataFrame(df)
        dataframe.to_csv("C:/Users/82102/OneDrive/문서/Emotion-Recognization/News_Crawling/NK/db_news_data.csv",index=False, header=True)
        
        self.replace_into_db(df)
    

if __name__ == '__main__':                      #main 함수를 의미
    dbu = DBUpdater()                           #DBUpdater 객체 생성 
    
    dbu.find_text('003490')                     #대한항공 코드
