from selenium import webdriver # For Selenium
from urllib.request import urlopen
from bs4 import BeautifulSoup # For BeautifulSoup
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import time

class Google:
    def __init__(self):

        # setting 크롤링 시 기기차단 우회 headers 옵션의 User-Agent 값을 커스터마이징 하여 보내도록 한다.
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("user-agent={Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36}")
 
        # Chrome 가상 driver 열기 
        self.driver = webdriver.Chrome('C:/Users/82102/chromedriver.exe') #chromedriver 로드
        self.driver.implicitly_wait(3) # 웹 페이지 전체가 넘어올 때까지 기다리기 
        #self.driver.maximize_window()  # window size 지정 (maximize)
        
    def __del__(self):
        self.driver.close()
        
    def search_keyword(self):

        ## 구글 홈 ##
        self.driver.get("https://www.google.com")
        company = self.driver.find_element_by_name("q")
        
        #현재 커서가 위치한 곳에 대한항공 입력하겠다.
        company.send_keys("대한항공")
        
        #Enter키 누른다
        company.send_keys(Keys.RETURN)
        
    def get_content(self,i,j):
        
        time.sleep(1)
        
        #도구 클릭
        menu=self.driver.find_element_by_id('hdtb-tls')
        menu.click()
        
        time.sleep(1)
        
        #모든날짜 클릭
        spread_menu = self.driver.find_elements_by_class_name("KTBKoe")
        spread_menu[1].click()
        
        time.sleep(1)
        
        #기간설정 클릭
        set_time = self.driver.find_element_by_xpath("//*[@id='lb']/div/g-menu/g-menu-item[7]")
        set_time.click()
        
        time.sleep(1)
        
        #시작일 설정
        start = self.driver.find_element_by_xpath("//*[@id='OouJcb']")
        start.send_keys(str(i)+"/"+str(j)+"/2021")
                    
        #종료일 설정
        end = self.driver.find_element_by_xpath("//*[@id='rzG2be']")
        end.send_keys(str(i)+"/"+str(j)+"/2021")
                    
        #실행버튼 클릭
        play = self.driver.find_element_by_xpath("//*[@id='T3kYXe']/g-button")
        play.click()

        #도구 클릭
        menu=self.driver.find_element_by_id('hdtb-tls')
        menu.click()
        
        time.sleep(1)
        
        #검색결과 개수 가져오기
        '''
        오류 . 일치하는 검색결과가 없습니다
        예외처리 -> try except
        '''
        try:
            result = self.driver.find_element_by_id("result-stats").text
            result=result[:result.find('개')]
            print("date: 2021."+str(i)+"."+str(j)+ " Search : "+result)
            #re.sub 검색량만 남기고 제거
            result = re.sub(r'[^0-9]', '', result)
        except:
            result='0'     
                
        time.sleep(1)
        
        #뒤로가기
        self.driver.back()
        
        return result

    def content(self):

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
        dataframe.to_csv("Search_Volume.csv",index=False, header=True)

if __name__ == "__main__":
    google = Google()    
    google.content()