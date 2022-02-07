""" 주식종목 뉴스(네이버 파이넌스) Crawling 하기 """  
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os 

import urllib3
urllib3.disable_warnings()

def find_lastpage(type,company_code):  
    '''
    find_lastpage() 함수: 마지막 페이지 찾는 함수
            input parameter : (str)type, (str)company_code
            output : (str)last_page
    '''
    
    #뉴스와 시세 데이터의 페이지
    if type=="news":
        url=f"https://finance.naver.com/item/news_news.naver?code={company_code}"
    elif type=="price":
        url=f"https://finance.naver.com/item/sise_day.naver?code={company_code}"       
    while True:   
        #User-agent : 크롤링 접속 차단 오류 방지
        html_news=BeautifulSoup(requests.get(url,verify=False,headers={'User-agent' : 'Mozilla/5.0'}).text, 'html.parser')   

        #pgRR 태그 - "맨뒤" 의미
        if html_news.find("td",class_="pgRR") != None:
            '''
            맨 뒤 클릭하면 맨 마지막 페이지로 바로 이동하지 않는다. 
            맨 뒤에 해당하는 태그가 없을 때까지 마지막 페이지로 이동
            '''
            td_tag = html_news.find("td",class_="pgRR")
            a_tag = td_tag.find("a")       
            url = "https://finance.naver.com/"+a_tag['href']
        else:
            '''
            "pgRR" 태그가 없다면 "on"태그의 text가 마지막 페이지를 의미 
            '''          
            last_page=html_news.find("td",class_="on").get_text()
            break
            
    return last_page

def cleaning(type,df):
    '''
    cleaning() 함수: 2021년 1년의 데이터만 가져오는 함수
            input parameter : (str) type, (str)df
            output : (str)df
    '''
    
    str=df
    for i in range(len(str['date'])):
        str['date'][i]=str['date'][i].replace('.',"")
        if type=="news":
            str['date'][i]=int(str['date'][i][3:9])
        elif type=="price":
            str['date'][i]=int(str['date'][i][1:9])

        #2021년에 해당하는 1년의 데이터만 크롤링 하기 위해
        if str['date'][i]>=220101:
            df=df.drop(index=[i],axis=0)
    
    return df

def cleaning_text(df):
    '''
    cleaning_text() 함수: 특수문자 공백 반복적인 마침표 제거
            input parameter : (str)df
            output : (str)df
    '''
    
    while ('.' in df):
        df = df.replace('.', '')
    df = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]',' ', df)
    df = ' '.join(df.split()).rstrip()
    
    return df

def find_url(company_code):
    '''
    find_url() 함수: 모든 기사 링크를 찾아 link_result 배열에 저장하는 함수
            input parameter : (str)company_code
            output : (list)link_result
    '''
    
    page=1
    link_result=[]
    #마지막 페이지
    last_page=find_lastpage("news",company_code)   
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
    
def find_text(company_code):
    '''
    find_text() 함수: 뉴스.공시 데이터 크롤링
            input parameter : (str)company_code
            output : (DataFrame)dataframe
    '''
    
    df=pd.DataFrame(columns={"date","title","content"})
    link_result=find_url(company_code)
    
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
        title = cleaning_text(title)
        title = ' '.join(title.split())
        content = cleaning_text(content)
        content = ' '.join(content.split())
        
        #data_list
        data_list={"date":time,"title":title,"content":content}   
        df=df.append(data_list,ignore_index=True)
        
    df=df[["date","title","content"]]   
    
    #cleaning 함수 날짜 처리 
    df=cleaning("news",df)
    
    dataframe=pd.DataFrame(df)
    dataframe.to_csv("C:/Users/82102/OneDrive/문서/Emotion-Recognization-fork/News_Crawling/NK/news_crawling.csv",index=False, header=True)
    
    return dataframe
    
def price_crawling(company_code):
    '''
    find_text() 함수: 시세 데이터 크롤링
            input parameter : (str)company_code
            output : (pandas.core.frame.DataFrame)dataframe
    '''
    
    df = pd.DataFrame() 
    
    #26페이지까지 없는 기업의 경우 last_page찾아서 입력
    last_page=find_lastpage("price",company_code)
    if int(last_page)>26:
        last_page =  26
    url = f"https://finance.naver.com/item/sise_day.naver?code={company_code}"
    
    for page in range(1, int(last_page) + 1):    
        pg_url = '{}&page={}'.format(url, page)     
        df = df.append(pd.read_html(requests.get(pg_url, headers = {'User-agent' : 'Mozilla/5.0'}).text)[0],ignore_index=True) 
        
    '''
    nan값 처리, 인덱스 값 초기화, 불필요한 인덱스 열 -> 제거
    각 항목 이름 설정 -> 영어로 (cleaning 함수 동일 사용)
    '''    
    df = df.dropna()  
    df=df.reset_index()
    df=df.drop(['index'],axis=1)
    df = df[['날짜','종가','전일비','시가','고가','저가','거래량']]   
    df = df.rename(columns={'날짜':'date','종가':'close','전일비':'diff','시가':'open','고가':'high','저가':'low','거래량':'volume'})   #각 칼럼의 이름을 영문으로 바꿈
    
    #전일비 계산 (+,- 고려 위해)
    for i in range(1,len(df['close'])):      
        df['diff'][i-1]=int(df['close'][i-1])-int(df['close'][i])
    
    #cleaning 함수 날짜 처리 
    df=cleaning("price",df)
    
    dataframe = pd.DataFrame(df)
    dataframe.to_csv("C:/Users/82102/OneDrive/문서/Emotion-Recognization-fork/News_Crawling/NK/price_crawling.csv",header=True,index=False)
    
    return dataframe
    
def main():
    company = input("종목 코드 입력: ")        #대한항공 003490 
    
    #dataframe 확인해보기 위해 각각 저장
    news_df=find_text(company)  
    price_df=price_crawling(company)
    
    return news_df,price_df

news_df,price_df=main() 
