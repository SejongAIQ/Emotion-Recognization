# from typing import Counter 
import pandas as pd                             
# from datetime import datetime, timedelta        # 날짜/시간 라이브러리
from bs4 import BeautifulSoup              # html 파일 관리 라이브러리
from selenium import webdriver             # selenium module import
from selenium.webdriver.common.keys import Keys

import urllib3
urllib3.disable_warnings()

class Crawling:
    # 초기화 함수
    def __init__(self): 
        
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

    # chrome 가상 driver 닫기
    def __del__(self):   
        self.driver.close()       

    # keyword 검색 함수
    def enter_keyword(self, keyword):
        search_btn = self.driver.find_element_by_xpath('//*[@id="stock_items"]')
        # keyword 검색
        search_btn.send_keys(keyword)
        self.driver.implicitly_wait(3)
        # Enter
        search_btn.send_keys(Keys.ENTER)            

    # 뉴스 데이터 크롤링 함수 
    def news_content_crawling(self, keyword):  

        # 뉴스.공시 tab click
        self.driver.find_element_by_xpath('#content > ul > li:nth-child(5) > a > span').click()

        df = pd.DataFrame(columns={"date", "title", "content"})           # df 생성

        # 한 페이지의 뉴스.공시 크롤링
        
        # 페이지 이동 - 마지막 페이지까지
                                     
        # News data csv 파일로 저장  
        news_df = pd.DataFrame(df)
        news_df.to_csv(keyword + "_news_data.csv", index = False, header = True)

    def price_data_preprocessing(self, df, keyword):
        # 시세 데이터 label화 및 날짜 순서대로 정리


        price_processing = pd.DataFrame(df)
        price_processing.to_csv(keyword+'_price_preprocessing_data.csv', index=False, head=True)


    # 시세데이터 crawling
    def price_data_crawling(self, keyword):

        # 시세 tab click
        self.driver.find_element_by_xpath('#content > ul > li:nth-child(2) > a > span').click()

        # 일별 시세 url로 이동


        df = pd.DataFrame(columns={"date", "price", "label"})


        # 내가 원하는 날짜까지 크롤링

        price_df = pd.DataFrame(df)
        price_df.to_csv(keyword + '_price_data.csv', index = False, head = True)
        
        # price data 전처리 및 라벨화
        self.price_data_preprocessing(price_df)

    
if __name__ == "__main__":
    # crawling class 선언
    info = Crawling()
    #news.example()
    
    # keyword 검색
    keyword = 'NCSOFT'
    info.enter_keyword(keyword)

    # keyword news crawling
    info.news_content_crawling(keyword)

    # keyword 시세 데이터 crawling
    info.price_data_crawling(keyword)
    