from selenium import webdriver # For Selenium
from urllib.request import urlopen
from bs4 import BeautifulSoup # For BeautifulSoup
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import time
import requests

import urllib3
urllib3.disable_warnings()

class Google:
    def __init__(self):
        '''
        __init__() : 초기화 함수
                    chrome webdriver open 및 구글 열기
        '''

        # setting 크롤링 시 기기차단 우회 headers 옵션의 User-Agent 값을 커스터마이징 하여 보내도록 한다.
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("user-agent={Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36}")
 
        # Chrome 가상 driver 열기 
        self.driver = webdriver.Chrome('C:/Users/82102/chromedriver.exe') #chromedriver 로드
        self.driver.implicitly_wait(3) # 웹 페이지 전체가 넘어올 때까지 기다리기 
        #self.driver.maximize_window()  # window size 지정 (maximize)
        
    def __del__(self):
        '''
        __del__() : 소멸자 함수
                    crawling 작업이 끝난 후 chrome webdriver 닫기
        '''

        self.driver.close()
        
    def search_keyword(self):
        '''
        search_keyword() : 종목 keyword로 google 검색창에 검색하기
        '''

        ## 구글 홈 ##
        self.driver.get("https://www.google.com")
        company = self.driver.find_element_by_name("q")
        
        #현재 커서가 위치한 곳에 대한항공 입력하겠다.
        company.send_keys("대한항공")
        
        #Enter키 누른다
        company.send_keys(Keys.RETURN)
        
    def get_content(self,i,j):
        '''
        get_content() 함수: 일별 구글 검색결과 crawling 함수
                input parameter : (int)i,j
                output : (str)result
        '''
        k=0
            
        #도구 클릭
        menu=self.driver.find_element_by_id('hdtb-tls')
        menu.click()
        time.sleep(2)
            
        #모든날짜 클릭
        spread_menu = self.driver.find_elements_by_class_name("KTBKoe")
        spread_menu[1].click()
        time.sleep(2)

        #기간설정 클릭
        set_time = self.driver.find_element_by_xpath("//*[@id='lb']/div/g-menu/g-menu-item[7]")
        set_time.click()
        time.sleep(2)

        start = self.driver.find_element_by_xpath("//*[@id='OouJcb']")
        start.send_keys(str(i)+"/"+str(j)+"/2021")

        end = self.driver.find_element_by_xpath("//*[@id='rzG2be']")
        end.send_keys(str(i)+"/"+str(j)+"/2021")
            
        time.sleep(2)

        #실행버튼 클릭
        play = self.driver.find_element_by_xpath("//*[@id='T3kYXe']/g-button")
        play.click()

        time.sleep(2)

        #도구 클릭
        menu=self.driver.find_element_by_id('hdtb-tls')
        menu.click()

        time.sleep(2)
            
        #검색결과
        try:
            result = self.driver.find_element_by_id("result-stats").text
            result=result[:result.find('개')]
            #re.sub 검색결과만 남기고 제거
            result = re.sub(r'[^0-9]', '', result)
        except:
            result='0'  
            
        time.sleep(2)
            
        '''
        "원하시면 생략된 결과를 포함하여 다시 검색하실 수 있습니다." 링크 이동으로 인한
        검색결과 불일치 . 해당 문구는 마지막 페이지까지 가야 나온다 
            
        해당 페이지가 마지막 페이지가 아니라면 마지막 페이지로 이동
        생략된 결과를 포함하여 다시 검색 링크 있다면 해당 링크로 이동
            
        1페이지에서 나온 검색결과와 마지막페이지에서 나온 검색결과 다르다 
        마지막 페이지의 검색결과를 가져와야 정확
        '''
            
        for i in range(2):
            #1. 마지막 페이지?
            while True:  
                page_html = self.driver.page_source
                soup = BeautifulSoup(page_html, 'html.parser')
                last=soup.select_one('#pnnext')
                if last==None:
                    break
                a_tag =soup.select_one('#pnnext')
                url="https://www.google.com"+a_tag['href']
                self.driver.get(url)
                k+=1

            time.sleep(2)

            #2. 생략된 검색결과?
            while True:
                page_html = self.driver.page_source
                soup = BeautifulSoup(page_html, 'html.parser')
                more = soup.select_one('#ofr > i > a')
                if more == None:
                    break
                a_tag =soup.select_one('#ofr > i > a')
                url="https://www.google.com"+a_tag['href']
                self.driver.get(url)
                k+=1
            
        '''
        일치하는 검색결과가 없습니다 -> 검색결과 0
        예외처리 -> try except
        '''
            
        time.sleep(2)
            
        if k>=1:
            #도구 클릭
            menu=self.driver.find_element_by_id('hdtb-tls')
            menu.click()
            time.sleep(2)
        
        try:
            #검색결과 가져오기
            result = self.driver.find_element_by_id("result-stats").text
            result=result[:result.find('개')]
            #re.sub 검색량만 남기고 제거
            result = re.sub(r'[^0-9]', '', result)
        except:
            result='0'     
            
        print("date : 2021."+str(i)+"."+str(j)+"Search"+str(result))
        time.sleep(2)

        for i in range(k):
            #뒤로가기
            self.driver.back()
            time.sleep(2)
                    
        time.sleep(2)
            
        #뒤로가기
        self.driver.back()
            
        return result
        

    def content(self):
        '''
        content() 함수: 날짜 지정 및 csv파일 생성
        '''

        # 구글 대한항공 겁색
        self.search_keyword()  
        
        df=pd.DataFrame(columns={"date","Search"})
        
        #2021년 1년치 검색량 
        for i in range(1,13):
            if i==2 or i==4 or i==6 or i==9 or i==11:
                if i==2:
                    for j in range(1,29):
                        result = self.get_content(i,j)
                        data_list={"date":"2021."+str(i)+"."+str(j),"Search":result}  
                        df=df.append(data_list,ignore_index=True)
                else:
                    for j in range(1,31):
                        result = self.get_content(i,j)
                        data_list={"date":"2021."+str(i)+"."+str(j),"Search":result}  
                        df=df.append(data_list,ignore_index=True)
            else:
                for j in range(1,32):
                    result = self.get_content(i,j)
                    data_list={"date":"2021."+str(i)+"."+str(j),"Search":result}   
                    df=df.append(data_list,ignore_index=True)
                    
        dataframe=pd.DataFrame(df)
        dataframe.to_csv("C:/Users/82102/OneDrive/바탕 화면/SJU/AI_Quant/daily_search.csv",index=False, header=True)

if __name__ == "__main__":
    google = Google()
    google.content()