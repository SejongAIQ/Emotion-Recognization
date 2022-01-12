""" 주식종목 뉴스(네이버 파이넌스) Crawling 하기 """  
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os 
from datetime import datetime
from datetime import timedelta

#뉴스 크롤링
date = (datetime.today()-timedelta(8)).strftime("%Y%m%d")
page = 1 
cnt=0
url_list=[]
link_result =[]
while True:
    if cnt==132: break      
    url=f"https://finance.naver.com/item/news_news.naver?code=003490&page={page}&sm=title_entity_id.basic&clusterId="
    source_code = requests.get(url).text
    html = BeautifulSoup(source_code, "lxml")
    # 뉴스 링크
    links = html.select('.title')     
    for link in links: 
        add = 'https://finance.naver.com' + link.find('a')['href']
        link_result.append(add)
    page += 1 
    cnt+=1
print(len(link_result))

df=pd.DataFrame(columns={"date","title","content"})

for i in range(len(link_result)):
    url=link_result[i]
    html_news=BeautifulSoup(requests.get(url,verify=False,headers={'User-agent' : 'Mozilla/5.0'}).text,"lxml")
    time=html_news.find("span",class_="tah p11").get_text()
    title=html_news.find("strong",{"class": "c p15"}).get_text()   
    content=html_news.find(id="news_read").get_text()
    if html_news.find("div",class_="link_news") != None:
        remove=html_news.find("div",class_="link_news").get_text()
        content=content.replace(remove,"")
    data_list={"date":time,"title":title,"content":content}   
    #print(i, data_list)
    df=df.append(data_list,ignore_index=True)
df=df[["date","title","content"]]
print(df) 

str=df
for i in range(len(str['date'])):
    str['date'][i]=str['date'][i].replace('.',"")
    str['date'][i]=int(str['date'][i][1:9])
    if str['date'][i]>=20220101:
        df=df.drop(index=[i])

dataframe=pd.DataFrame(df)
dataframe.to_csv("C:/Users/82102/OneDrive/바탕 화면/SJU/AI_Quant/news_final.csv",index=False, header=True)

#시세 크롤링
df = pd.DataFrame() 
lastpage = 26
url = f"https://finance.naver.com/item/sise_day.naver?code=003490"         
for page in range(1, lastpage + 1):    
    pg_url = '{}&page={}'.format(url, page)                                
    df = df.append(pd.read_html(requests.get(pg_url, headers = {'User-agent' : 'Mozilla/5.0'}).text)[0])                    
                                                                                   
df = df.dropna()                                                                                                                  
df = df[['날짜','종가','전일비','시가','고가','저가','거래량']]   
dataframe = pd.DataFrame(df)
dataframe.to_csv("C:/Users/82102/OneDrive/바탕 화면/SJU/AI_Quant/day_price.csv",header=True,index=False)

df