# Module import

import re                                       # For Data Cleaning 
import requests                                 # For Html Access
import pandas as pd                             # For Data Management
from bs4 import BeautifulSoup                   # For Html Management

import urllib3                                  # For urllib3 Error Prevention 
urllib3.disable_warnings()

class News:

    # 데이터 정제 함수  
    def cleaning(self,raw_data):  

        '''
        cleaning() : 데이터 정제 함수
            input parameter : (Series) raw_data
            output : (Series) raw_data
        '''

        cleaned_title = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]',' ', raw_data['title'])
        cleaned_content = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]',' ', raw_data['content'])
        raw_data['title'] = ' '.join(cleaned_title.split()).rstrip()
        raw_data['content'] = ' '.join(cleaned_content.split()).rstrip()

        return raw_data

    # 마지막 페이지 url 추출 함수
    def find_last_url(self, url):

        '''
        find_last_url() : 마지막 페이지 url 추출 함수 
            input parameter : (str) url
            output : (str) last_url
        '''

        while True:

            # 맨뒤 페이지 html 가져오기 
            url_html = BeautifulSoup(requests.get(url, verify=False, headers = {'User-agent' : 'Mozilla/5.0'}).text,"lxml")
            
            # pgRR 태그가 존재하는 경우
            if url_html.select('td.pgRR > a'): 
                href = url_html.select('td.pgRR > a')[0]['href']
                url = f"https://finance.naver.com{href}"           

            # on 태그가 존재하는 경우 ( 맨 마지막 페이지 )
            else: 
                href = url_html.select('td.on > a')[0]['href']
                last_url = f"https://finance.naver.com{href}" 

                return last_url

    ## 한 종목의 뉴스 url list 반환 함수 ##
    def read_news_url(self,code): 

        '''
        read_news_url() : 한 종목의 뉴스 url list 반환 함수 
            input parameter : (str) code
                lastpage 추출을 위한 find_last_url 함수 호출
                last_url과 현재 url이 일치할 경우 종료
            output : (list) news_url
        '''
    
        page =  1                             
        url_list = []                          

        try:
            while True:
                # 네이버 금융 글로벌 경제 url 
                url=f"https://finance.naver.com/item/news_news.naver?code={code}&page={page}&sm=entity_id.basic&clusterId="
                html_news = BeautifulSoup(requests.get(url, verify=False, headers = {'User-agent' : 'Mozilla/5.0'}).text,"lxml")

                # lastpage url 로드
                if page == 1: 
                    href = html_news.select('td.pgRR > a')[0]['href']
                    pgRR_url = f"https://finance.naver.com{href}" 
                    last_url = news.find_last_url(pgRR_url)
                    
                # 전체 a 태그 로드 
                a_tag_list = html_news.select('table.type5 > tbody > tr > td > a')     
               
                # 전체 뉴스 url 저장 
                for i in range(len(a_tag_list)):                       
                    news_url = a_tag_list[i]['href']                   
                    url_list.append(news_url)

                # [종료 조건] last_url과 현재 url이 일치할 경우 종료.
                if last_url == url:                                     
                    return url_list 

                # 데이터 업데이트     
                page = page + 1                                               
 
        except Exception as e:                                          
            print('Exception occured :', str(e))
            return None

    ## 한 종목의 뉴스 데이터 크롤링 함수 ##
    def news_content_crawling(self,code,company):  

        '''
        news_content_crawling() : 한 종목의 뉴스 데이터 크롤링 함수 
            input parameter : (str) code, (str) company
                url_list 반환을 위한 read_news_url 함수 호출
                데이터 정제를 위한 cleaning 함수 호출 
            output : (csv) 한 종목의 1년 뉴스 데이터 
        '''

        # 데이터를 저장할 df 생성 
        df = pd.DataFrame(columns={"date","title","content"})  
        # url_list 로드          
        url_list = news.read_news_url(code)                           

        for i in range(len(url_list)):                                  
            
            # 해당 뉴스 url의 html 파일 읽어오기 
            url=f"https://finance.naver.com{url_list[i]}"                   
            html_news = BeautifulSoup(requests.get(url, verify=False, headers = {'User-agent' : 'Mozilla/5.0'}).text,"lxml")  

            # time, title, content 데이터 크롤링 
            time = html_news.find("span",class_ = "tah p11").get_text()     
            title = html_news.find("strong",class_ = 'c p15').get_text()    
            content = html_news.find("div",class_ = "scr01").get_text()     
            
            # Series 형태로 데이터 저장 
            data_list = {"date":time, "title":title, "content":content}    
            # 데이터 정제 후, 데이터 추가 
            data_list = news.cleaning(data_list)                            
            df = df.append(data_list, ignore_index=True)                   

            # 다운로드 현황 출력 
            print('[news_data]::({}) {}/{} pages are downloading...'.format(company,i+1,len(url_list))) 
        
        # 최종 데이터 column 순서 정리 후, csv 파일로 저장 
        df = df[["date","title","content"]]                          
        df.to_csv(f"C:/Users/user/OneDrive/바탕 화면/AI_QUANT/DATA/[{company}]news_data.csv",header=False,index=False)

    ## 섹터별 데이터 로드 함수 ## 
    def load_news_by_sector(self):   

        '''
        news_content_crawling() : 섹터별 데이터 로드 함수  
            input parameter :
                한 종목의 뉴스 데이터를 csv로 저장하기 위해 news_content_crawling 함수 호출
            output : 전 종목 뉴스 데이터 크롤링 완료
        '''

        # 업종별 코드 로드 
        codes_list = pd.read_csv('C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/code_by_Sector.csv', encoding = 'cp949')     

        # NaN 데이터 삭제                          
        codes_list = codes_list.dropna()
        # 전체 데이터 string으로 형 변환                    
        codes_list = codes_list.applymap(str)          

        # 종목별 뉴스 데이터 크롤링 함수 실행 
        for i in range(len(codes_list)):
            print(f"[{codes_list['code'][i]}] Start news data Crawling" )
            # code 자리수 6개로 고정 
            news.news_content_crawling(codes_list['code'][i].zfill(6),codes_list['company'][i])      


if __name__ == "__main__":
    news = News()
    news.load_news_by_sector()





