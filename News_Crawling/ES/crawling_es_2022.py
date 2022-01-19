# from typing import Counter 
import pandas as pd          
import requests                   
# from datetime import datetime, timedelta        # 날짜/시간 라이브러리
from bs4 import BeautifulSoup              # html 파일 관리 라이브러리
from selenium import webdriver             # selenium module import
from selenium.webdriver.common.keys import Keys
# import re

import urllib3
urllib3.disable_warnings()

class Crawling:
    def __init__(self): 
        '''
        __init__() : 초기화 함수
                    chrome webdriver open 및 네이버 금융 사이트 열기
        '''
        
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--diable-dev-shm-usage")
        self.options.add_argument("user-agent={Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36}")

        # chrome 가상 driver 열기
        self.driver = webdriver.Chrome('/Users/eesun/Downloads/chromedriver', options = self.options)
        self.driver.implicitly_wait(1)
        self.driver.maximize_window()

        # 네이버 금융 사이트
        self.driver.get("https://finance.naver.com/")
        self.driver.implicitly_wait(1)

        # 각 dataframe 초기화
        self.news_data = pd.DataFrame(columns={"date", "title", "content"})  
        self.price_raw_data = pd.DataFrame(columns={"date", "price"})  
        self.price_data = pd.DataFrame(columns={"date", "price", "label"})  


    def __del__(self):   
        '''
        __del__() : 소멸자 함수
                    crawling 작업이 끝난 후 chrome webdriver 닫기
        '''
        
        self.driver.close()       


    def enter_keyword(self, keyword):
        '''
        enter_keyword() : 종목 keyword로 검색하기
            input parameter : (str)keyword
            output : None
        '''

        # 검색창 찾기
        search_btn = self.driver.find_element_by_xpath('//*[@id="stock_items"]')

        # keyword 검색
        search_btn.send_keys(keyword)
        self.driver.implicitly_wait(3)

        # Enter
        search_btn.send_keys(Keys.ENTER)    


    def extract_code(self, keyword):
        '''
        extract_code() : 특정 종목 Keyword에 해당하는 code 추출하기
            input parameter : (str)keyword
            output : (str)code
        '''

        # [논의] keyword code 가져오기
        '''
        current url의 code 뒷 부분을 뽑아오려고 하였으나, 
        일반화를 위해 iloc, loc는 사용하고 싶지 않았고
        다른 방법은 생각이 안났다 !!
        ex) https://finance.naver.com/item/main.naver?code=036570
        에서 code= 뒷 부분

        # current url 가져오기
        cur_url = self.driver.current_url
        '''
        code = self.driver.find_element_by_css_selector('#middle > div.h_company > div.wrap_company > div > span.code').text
        
        return code


    def save_news_url(self, url):
        '''
        save_news_url() : 특정 종목의 각 뉴스.공시 데이터 url 저장 함수
            input parameter : (str) 뉴스.공시 page url
            output : 각 공시의 page url list
        '''

        url_list = []

        # url내의 html 내용을 끌어오기     
        html = requests.get(url)
        news_html = BeautifulSoup(html.text, 'html.parser')

        #a 태그 로드 
        a_tag_list = news_html.select('table.type5 > tbody > tr > td > a')     
        for i in range(len(a_tag_list)):
            # 각 뉴스 url
            news_url = a_tag_list[i]['href']  
            # 각 뉴스 url를 list에 담기 
            url_list.append(news_url)

        return url_list

    
    def news_data_crawling(self, url):
        '''
        news_data_crawling() : 한 페이지의 뉴스.공시 데이터 크롤링
            input parameter : (str) 크롤링 할 url
            output : news_data dataframe에 crawling한 값 저장(update)
        '''

        # url내의 html 내용을 끌어오기     
        html = requests.get(url)
        news_html = BeautifulSoup(html.text, 'html.parser')

        # 날짜, 제목, 기사내용 저장
        date = news_html.find("span",class_ = "tah p11").get_text()
        title = news_html.find("strong",class_ = 'c p15').get_text()
        content = news_html.find("div",class_ = "scr01").get_text()

        # crawling data update
        crawl_dict = {"data":date, "title":title, "content":content}
        self.news_data = self.news_data.append(crawl_dict, ignore_index=True)


    def news_crawling(self, keyword, code):  
        '''
        news_crawling() : 특정 종목 뉴스.공시 데이터 크롤링 전체 함수
            input parameter : (str)keyword, (int)code
                각 뉴스.공시 페이지 Url 가져오기 위해 save_news_url()함수 호출
                한 페이지 크롤링하기 위한 news_data_crawling()함수 호출
            output : (csv)news_df
        '''

        cur_page = 1
        url = f"https://finance.naver.com/item/news_news.naver?code={code}"
        self.driver.get(url)
        self.driver.implicitly_wait(1)

        # [확인] 현재 페이지가 안 불러와지나 확인하기 !
        # -> 현재 페이지가 안 불러와진 경우 for page in pages 전에 현재 페이지 크롤링 해야함

        while True:
            
            # page bar class 찾기
            page_bar = BeautifulSoup.select(selector='body > div > table.Nnavi > tbody > tr')
            # page_bar = self.driver.find_element_by_class_name("Nnavi")
            print(page_bar)
            
            # page 수(a태그) 객체 저장
            pages = page_bar.find_element_by_class_name('a')
            now_page = page_bar.find_element_by_class_name('on').text

            # 현재 나와있는 페이지 수까지 이동
            for page in pages:
                # 뉴스.공시 Page url
                url = f"https://finance.naver.com/item/news_news.naver?code={code}&page={cur_page}"

                page_num = page.text.strip()

                if page_num in ['맨앞', '이전', '맨뒤']:
                    pass
                elif page_num == '다음':
                    # 다음을 누르기
                    cur_page += 1
                    page.send_keys("\n")
                    self.driver.implicitly_wait(3)
                    break
                elif int(page_num) > int(now_page):

                    # 각 뉴스.공시 page url 저장
                    url_list = self.save_news_url(url)

                    # 한 페이지의 뉴스.공시 크롤링
                    for idx in range(len(url_list)):
                        self.news_data_crawling(url_list[idx])

                    # 다음 페이지로 넘어가기
                    cur_page += 1
                    page.send_keys('\n')
                    self.driver.implicitly_wait(3)
                    continue
                else:
                    # 마지막 페이지인 경우
                    is_done = True
                    break

            if is_done == True:
                break

                                     
        # News data csv 파일로 저장  
        news_df = pd.DataFrame(self.news_data)
        news_df.to_csv(keyword + "_news_data.csv", index = False, header = True)



    def price_data_preprocessing(self, df, keyword):
        '''
        price_data_preprocessing() : 크롤링한 시세 데이터 전처리 함수
                                    시세 데이터 label화 및 날짜 순서대로 정리
            input parameter : 크롤링한 시세 데이터(df), (str)keyword
            output : (csv)price_processing
        '''

        # 날짜 순서대로 정렬

        # 라벨화


        # 내가 원하는 날짜까지 추출


        price_processing = pd.DataFrame(df)
        price_processing.to_csv(keyword+'_price_preprocessing_data.csv', index=False, head=True)


    def price_data_crawling(self, keyword, code):
        '''
        price_data_crawling() : 특정 종목 시세 데이터 크롤링 함수
            input parameter : (str)keyword, (str)code
                시세 데이터 라벨링 및 전처리를 위한 price_data_preprocessing 호출
            output : (csv)price_raw_df
        '''

        # 일별 시세 url
        cur_page = 1
        url = f"https://finance.naver.com/item/sise_day.naver?code={code}&page={cur_page}"
        self.driver.get(url)
        self.driver.implicitly_wait(1)

        # [확인] 현재 페이지가 안 불러와지나 확인하기 !
        # -> 현재 페이지가 안 불러와진 경우 for page in pages 전에 현재 페이지 크롤링 해야함

        while True:
            
            # page bar class 찾기
            page_bar = self.driver.find_element_by_class_name("Nnavi")
            
            # page 수(a태그) 객체 저장
            pages = page_bar.find_element_by_class_name('a')
            now_page = page_bar.find_element_by_class_name('on').text

            print("pages :", pages)
            print("now page :", now_page)

            # 현재 나와있는 페이지 수까지 이동
            for page in pages:
                # 시세 데이터 Page url
                url = f"https://finance.naver.com/item/sise_day.naver?code={code}&page={cur_page}"

                page_num = page.text.strip()

                if page_num in ['맨앞', '이전', '맨뒤']:
                    pass
                elif page_num == '다음':
                    # 다음을 누르기
                    cur_page += 1
                    page.send_keys("\n")
                    self.driver.implicitly_wait(3)
                    break
                elif int(page_num) > int(now_page):

                    # 한 페이지의 시세 데이터 저장
                    html = requests.get(url)
                    price_html = BeautifulSoup(html.text, 'html.parser')

                    # 날짜 및 시세 데이터 크롤링
                    date = price_html.find("span",class_ = "tah p10 gray03").get_text()
                    price = price_html.find("span",class_ = 'tah p11').get_text()

                    # crawling data update
                    crawl_dict = {"data":date, "price":price}
                    print(crawl_dict) ##
                    self.price_data = self.price_data.append(crawl_dict, ignore_index=True)

                    # 다음 페이지로 넘어가기
                    cur_page += 1
                    page.send_keys('\n')
                    self.driver.implicitly_wait(3)
                    continue
                else:
                    # 마지막 페이지인 경우
                    is_done = True
                    break

            if is_done == True:
                break

        # 크롤링한 시세 데이터 csv로 저장
        price_df = pd.DataFrame(self.price_data)
        price_df.to_csv(keyword + '_price_raw_data.csv', index = False, head = True)
        
        # price data 전처리 및 라벨화 함수 호출
        # self.price_data_preprocessing(price_df)

    
if __name__ == "__main__":
    '''
    Crawling class 실행
    '''

    # crawling class 선언
    info = Crawling()
    
    # keyword 검색
    '''
    추후에 keyword가 담겨있는 파일을 열어 Keyword 하나씩 받아오는 형식으로 진행
    '''
    keyword = 'NCSOFT'
    info.enter_keyword(keyword)

    # keyword에 해당하는 code 추출
    ##-- NCSOFT의 code는 036570 --##
    code = info.extract_code(keyword)
    print(code)

    # keyword 관련 news 데이터 crawling
    info.news_crawling(keyword, code)

    # keyword 관련 시세 데이터 crawling
    info.price_data_crawling(keyword, code)

    