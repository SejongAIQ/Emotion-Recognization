from turtle import pos
from selenium import webdriver 
from bs4 import BeautifulSoup                   # For Html Management
from selenium.webdriver.common.keys import Keys
from datetime import date, timedelta
import pandas as pd
import time 

class Posting_volume():
    ## 생성자 함수 ##
    def __init__(self):
        # Chrome 가상 driver 열기 
        self.driver = webdriver.Chrome('/Users/user/Downloads/chromedriver_win32/chromedriver.exe') # chromedriver 로드
        self.driver.implicitly_wait(3) # 웹 페이지 전체가 넘어올 때까지 기다리기 
        self.driver.maximize_window()  # window size 지정 (maximize)

        # 날짜 setting :: 오늘 
        self.date = date.today()
        
    ## 소멸자 함수 ##
    def __del__(self):
        # Chrome 가상 dirver 닫기
        self.driver.close()

    ## 키워드 검색을 위한 함수 ##
    def enter_keyword(self,company):

        '''
        enter_keyword() : 키워드 검색을 위한 함수 
            input parameter :  (String) company
            output : 키워드 검색 완료
        '''
        
        # google url 접속 시도 
        url = f"https://www.google.com"
        self.driver.get(url)
        # 웹 페이지 로딩 대기 
        time.sleep(0.5)

        # 검색 요소에 company 명 전송(입력)
        element = self.driver.find_element_by_name('q')
        element.send_keys(f"{company} 기업")
        # 엔터 효과 
        element.submit()
        time.sleep(0.5)

    
    ## 한 기업의 게시글량 크롤링 함수 ##
    def posting_volume_crawling(self,date,company):

        '''
        posting_volume_crawling() : 한 기업의 게시글 량 크롤링 함수  
            input parameter : (Date) date, (String) company
                키워드 검색을 위한 함수 호출 
                날짜 별 게시글 수 크롤링을 위한 함수 호출
            output : 한 기업의 일별 게시글량 csv 파일 저장 완료 
        '''

        # 게시글 수 저장 공간 
        df = pd.DataFrame(columns={"date","posting_volume"})

        # 키워드 검색을 위한 함수 호출 
        self.enter_keyword(company)

        # 날짜 별 게시글 수 크롤링
        for i in range(365):
        
            # 날짜 setting
            date = date - timedelta(1)
            enter_date = date.strftime("%m/%d/%Y")

            # [ 도구 -> 모든 기간 -> 기간 설정 -> 시작일 태그 ]
            
            # 도구 버튼 클릭 
            self.driver.find_element_by_css_selector('#hdtb-tls').click()
            time.sleep(0.5)

            # 기간 버튼 클릭 
            #hdtbMenus > span:nth-child(3) > g-popup > div.rIbAWc
            self.driver.find_element_by_css_selector('#hdtbMenus > span:nth-child(3) > g-popup > div.rIbAWc').send_keys(Keys.ENTER)
            time.sleep(0.5)

            # 기간 설정 클릭 -> 시작일, 종료일 입력 
            self.driver.find_element_by_css_selector('#lb > div > g-menu > g-menu-item:nth-child(7) > div > div > span').send_keys(Keys.ENTER)
            time.sleep(0.5)
            self.driver.find_element_by_css_selector('#OouJcb').send_keys(enter_date)
            time.sleep(0.5)
            self.driver.find_element_by_css_selector('#rzG2be').send_keys(enter_date)
            time.sleep(0.5)
            self.driver.find_element_by_css_selector('#T3kYXe > g-button').send_keys(Keys.ENTER)
            time.sleep(1) 

            # 현재 페이지 html 정보 가져오기 
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'lxml')

            # 날짜 별 게시글 수 크롤링 
            try:
                posting_volume = soup.find("div", id = "result-stats").get_text()[7:-10]
                data_list = {"date":enter_date, "posting_volume": posting_volume}
            except:
                posting_volume = 0
                data_list = {"date":enter_date, "posting_volume": posting_volume}

            # 데이터 추가 
            df = df.append(data_list, ignore_index=True)
            # 뒤로 가기
            self.driver.back()
        
        # 최종 데이터 colume 순서 정리 후, csv 파일로 저장 
        df = df[["date","posting_volume"]]
        df.to_csv(f"C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/DATA/Posting_volume/[{company} posting_volumn.csv")        
        
    ## 섹터별 데이터 로드 함수 ##
    def load_posting_volume_by_Sector(self):

        '''
        load_posting_volume_by_Sector() : 섹터별 데이터 로드 함수  
            input parameter :
                한 종목의 게시글 량 데이터 크롤링을 위한 posting_volume_crawling 함수 호출
            output : 전 종목 게시글 량 데이터 크롤링 완료
        '''

        # 업종별 코드 로드 
        codes_list = pd.read_csv('C:/Users/user/OneDrive/바탕 화면/CODE/AIQ_pork/News_Crawling/HJ/DATA/code_by_Sector.csv', encoding = 'cp949')     

        # NaN 데이터 삭제                          
        codes_list = codes_list.dropna()
        # 전체 데이터 string으로 형 변환                    
        codes_list = codes_list.applymap(str)          

        # 종목별 게시글량 데이터 크롤링 함수 실행 
        for i in range(len(codes_list)):
            print(f"[{codes_list['code'][i]}] Start news data Crawling" )
            self.posting_volume_crawling(self.date, codes_list['company'][i])  

if __name__ == '__main__' :
    posting = Posting_volume()
    posting.load_posting_volume_by_Sector()
