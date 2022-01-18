""" 주식종목 뉴스(네이버 파이넌스) Crawling 하기 """  
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os 

#함수화 진행 (done)
#마지막 페이지 이동 (done)
#데이터 전처리 - 날짜 조정 (done)
#데이터 전처리 - 불필요한 문자 제거 필요
#시세크롤링 (전일비 계산) (done + 26,27p)

def find_lastpage(type,company_code):
    if type=="news":
        url=f"https://finance.naver.com/item/news_news.naver?code={company_code}"
    elif type=='price':
        url=f"https://finance.naver.com/item/sise_day.naver?code={company_code}"
    while True:       
        html_news=BeautifulSoup(requests.get(url,verify=False,headers={'User-agent' : 'Mozilla/5.0'}).text,"lxml")
        #pgRR 태그 - "맨뒤" 의미
        if html_news.find("td",class_="pgRR") != None:
            td_tag = html_news.find("td",class_="pgRR")
            a_tag = td_tag.find("a")
            #맨 뒤 클릭하면 맨 마지막 페이지로 바로 이동하지 않는다. 
            #맨 뒤에 해당하는 태그가 없을 때까지 마지막 페이지로 이동
            url = "https://finance.naver.com/"+a_tag['href']
        else:
            #"pgRR" 태그가 없다면 "on"태그의 text가 마지막 페이지를 의미
            last_page=html_news.find("td",class_="on").get_text()
            break
    return last_page

def cleaning(type,df):
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

def find_url(company_code):
    page=1
    link_result=[]
    last_page=find_lastpage("news",company_code)
    #마지막 페이지
    while True:
        if page==int(last_page)+1: break      
        url=f"https://finance.naver.com/item/news_news.naver?code={company_code}&page={page}&sm=title_entity_id.basic&clusterId="
        source_code = requests.get(url).text
        html = BeautifulSoup(source_code, "lxml")
        # 뉴스 링크
        links = html.select('.title')    
        for link in links: 
            add = 'https://finance.naver.com' + link.find('a')['href']
            link_result.append(add)
        #link_result에 모든 기사 링크 저장
        page+=1
    return link_result
    
def find_text(company_code):
    df=pd.DataFrame(columns={"date","title","content"})
    link_result=find_url(company_code)
    for i in range(len(link_result)):
        url=link_result[i]
        #html_news
        html_news=BeautifulSoup(requests.get(url,verify=False,headers={'User-agent' : 'Mozilla/5.0'}).text,"lxml")
        #time
        time=html_news.find("span",class_="tah p11").get_text()
        #title
        title=html_news.find("strong",{"class": "c p15"}).get_text()   
        #content
        #link_news 태그의 내용이 함께 출력됨 -> 해당 태그 내용 remove 진행
        content=html_news.find(id="news_read").get_text()
        if html_news.find("div",class_="link_news") != None:
            remove=html_news.find("div",class_="link_news").get_text()
            content=content.replace(remove,"")    
        #data_list
        data_list={"date":time,"title":title,"content":content}   
        #df
        df=df.append(data_list,ignore_index=True)
    df=df[["date","title","content"]]   
    df=cleaning("news",df)
    dataframe=pd.DataFrame(df)
    dataframe.to_csv("News_Crawling/NK/update_newscrawling.csv",index=False, header=True)
    
def price_crawling(company_code):
    df = pd.DataFrame() 
    #시세데이터 1년치 -> 26페이지 까지 (2022년 데이터만 삭제해주기) -> 26페이지 마지막 날짜 전일비는 27페이지꺼 가져와야 한다
    #26페이지까지 없는 기업의 경우 last_page찾아서 입력
    last_page=find_lastpage("price",company_code)
    if int(last_page)>26:
        last_page =  26
    url = f"https://finance.naver.com/item/sise_day.naver?code={company_code}"
    for page in range(1, int(last_page) + 1):    
        pg_url = '{}&page={}'.format(url, page)     
        df = df.append(pd.read_html(requests.get(pg_url, headers = {'User-agent' : 'Mozilla/5.0'}).text)[0],ignore_index=True) 
    #nan값 처리
    df = df.dropna()  
    #인덱스 값 초기화
    df=df.reset_index()
    #인덱스 열 불필요 -> 제거
    df=df.drop(['index'],axis=1)
    df = df[['날짜','종가','전일비','시가','고가','저가','거래량']]     
    #각 항목 이름 -> 영어로 (cleaning 함수 동일하게 사용하기 위해)
    df = df.rename(columns={'날짜':'date','종가':'close','전일비':'diff','시가':'open','고가':'high','저가':'low','거래량':'volume'})   #각 칼럼의 이름을 영문으로 바꿈
    for i in range(1,len(df['close'])):
        df['diff'][i-1]=int(df['close'][i-1])-int(df['close'][i])
        #전일비 계산 (+,- 고려 위해)
    df=cleaning("price",df)
    dataframe = pd.DataFrame(df)
    dataframe.to_csv("News_Crawling/NK/update_pricecrawling.csv",header=True,index=False)
    
def main():
    company = input("종목 코드 입력: ")        #대한항공 003490 
    #마인즈랩 377480 - 총 페이지 수 3페이지 / 중간 결과물 보기 위해 
    find_text(company)  
    price_crawling(company)

main() 
