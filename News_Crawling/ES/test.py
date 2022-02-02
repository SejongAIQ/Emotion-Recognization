import pandas as pd
from selenium import webdriver             # selenium module import
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta # 현재 날짜를 가져오기 위한 라이브러리
import re
import time

class DailySearchVolume:

    def __init__(self):
        '''
        __init__() : 초기화 함수
                    chrome webdriver open 및 구글 열기
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
        self.driver.get("https://google.com/")
        
        self.driver.implicitly_wait(1)

        # dataframe 및 현재 날짜 초기화
        self.daily_search_volume = pd.DataFrame(columns={"date", "search_volume"})
        self.today_year = datetime.today().year
        self.today_month = datetime.today().month
        self.today_day = datetime.today().day


    # def __del__(self):   
    #     '''
    #     __del__() : 소멸자 함수
    #                 crawling 작업이 끝난 후 chrome webdriver 닫기
    #     '''
        
    #     self.driver.close()      


    def enter_keyword(self, keyword):
        '''
        enter_keyword() : 종목 keyword로 google 검색창에 검색하기
            input parameter : (str)keyword
            output : None
        '''

        # google 검색창 찾기
        search_btn = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')

        # keyword 검색
        search_btn.send_keys(keyword)
        self.driver.implicitly_wait(3)

        # Enter
        search_btn.send_keys(Keys.ENTER)    


    def make_valid_date(self, year, month, day):
        '''
        make_valid_date() : 기간 검색을 위한 유효한 날짜 string 생성
            input parameter : (int)year, (int)month, (int)day
            output : (str) date - 형식 : month/day/year
                    ex) 2020/01/14 => 14/1/2020
        '''
        return str(month)+'/'+str(day)+'/'+str(year)


    def save_format_date(self, year, month, day):
        '''
        make_valid_date() : 저장 날짜 string 생성
            input parameter : (int)year, (int)month, (int)day
            output : (str) date - 형식 : year.month.day
        '''
        if month < 10:
            if day < 10:
                return str(year)+'.0'+str(month)+'.0'+str(day)
            else:
                return str(year)+'.0'+str(month)+'.'+str(day)
        else:
            if day<10:
                return str(year)+'.'+str(month)+'.0'+str(day)
            else:
                return str(year)+'.'+str(month)+'.'+str(day)


    def update_date(self, year, month, day):
        '''
        update_date() : 조회 날짜 update 함수
            input parameter : (int)year, (int)month, (int)day
            output : update된 날짜
        '''
        
        date = datetime(year, month, day, 0, 0, 0)
        date = date + timedelta(days=1)

        return date.year, date.month, date.day


    def search_volume_crawling(self, keyword):  
        '''
        search_volume_crawling() : 특정 종목 일별 검색량 크롤링
            input parameter : (str)keyword
            output : (csv)news_df
        '''

        # 날짜 설정
        '''
        시작일, 종료일을 수기로 작성할 수 있음
            형식 - 2021.10.02 => 10/2/2021
        '''

        print("Today's date :", datetime.today().strftime("%Y/%m/%d"))



        year = 2022
        month = 1
        day = 31

        '''
        date = self.make_valid_date(year,month,day)
        print('valid date: ',date)

        # 도구 버튼 클릭
        self.driver.find_element_by_xpath('//*[@id="hdtb-tls"]').click()

        self.driver.implicitly_wait(3)
            
        # '모든 날짜' 버튼 클릭 - 일별 날짜를 가져오기 위함

        # self.driver.find_element_by_xpath('//*[@id="hdtbMenus"]/span[2]/g-popup/div[1]').click()
        self.driver.find_element_by_xpath('//*[@id="hdtbMenus"]/span[2]/g-popup/div[1]').send_keys(Keys.ENTER)
        self.driver.implicitly_wait(3)

        # '모든 날짜'의 '기간 설정' 클릭
        self.driver.find_element_by_xpath('//*[@id="lb"]/div/g-menu/g-menu-item[7]').click()
        self.driver.implicitly_wait(3)

        # '시작일' 입력
        start_date_btn = self.driver.find_element_by_xpath('//*[@id="OouJcb"]')
        start_date_btn.send_keys(date)

        # '종료일' 입력
        end_date_btn = self.driver.find_element_by_xpath('//*[@id="rzG2be"]')
        end_date_btn.send_keys(date)    

        # 실행
        search_btn = self.driver.find_element_by_xpath('//*[@id="T3kYXe"]/g-button ')
        search_btn.send_keys(Keys.ENTER) 

        self.driver.implicitly_wait(3)

        # 도구 버튼 클릭 - 조회하기 위함
        self.driver.find_element_by_xpath('//*[@id="hdtb-tls"]').click()

        # 일별 검색량 crawling
        save_date = self.save_format_date(year, month, day)
        volume = self.driver.find_element_by_css_selector('#result-stats').text
        volume = volume.replace("검색결과 약 ", '')
        volume = volume[:volume.index('개')]
        print('date: ', save_date)
        print('Volume: ', volume)
            
        # crawling date update
        crawl_dict = {"date":save_date, "search_volume":volume}
        self.daily_search_volume = self.daily_search_volume.append(crawl_dict, ignore_index=True)
        self.driver.implicitly_wait(3)
        self.driver.implicitly_wait(3)
        '''

        date = self.make_valid_date(year,month,day)
        print("\nSearch date :", date)

        # 도구 버튼 클릭
        self.driver.find_element_by_xpath('//*[@id="hdtb-tls"]').send_keys(Keys.ENTER)
        self.driver.implicitly_wait(3)

        # '모든 날짜' 버튼 클릭 - 일별 날짜를 가져오기 위함
        # self.driver.find_element_by_xpath('//*[@id="ow67"]/div/div/div/div').click()
        self.driver.find_element_by_xpath('//*[@id="hdtbMenus"]/span[2]/g-popup/div[1]').send_keys(Keys.ENTER)
        self.driver.implicitly_wait(3)

        # '모든 날짜'의 '기간 설정' 클릭
        self.driver.find_element_by_xpath('//*[@id="lb"]/div/g-menu/g-menu-item[7]').click()
        self.driver.implicitly_wait(3)

        # '시작일' 입력
        start_date_btn = self.driver.find_element_by_xpath('//*[@id="OouJcb"]')
        start_date_btn.send_keys(date)

        # '종료일' 입력
        end_date_btn = self.driver.find_element_by_xpath('//*[@id="rzG2be"]')
        end_date_btn.send_keys(date)    

        # 실행
        search_btn = self.driver.find_element_by_xpath('//*[@id="T3kYXe"]/g-button')
        search_btn.send_keys(Keys.ENTER) 
        self.driver.implicitly_wait(5)

        # 도구 버튼 클릭 - 조회하기 위함
        self.driver.find_element_by_xpath('//*[@id="hdtb-tls"]').send_keys(Keys.ENTER)
        time.sleep(4)


        # volume = self.driver.find_element_by_xpath('//*[@id="appbar"]').text
        # print('If Else')
        # print(volume)
        # if len(volume) == 0:
        #     print('No search Volume!')
        #     volume = 0
        # else:
        #     volume = volume[:volume.index('개')]
        #     # print(volume)
        #     volume = re.sub(r'[^0-9]', '', volume)
        #     volume = int(volume)
        # print("%s's Search Volume is %d"%(date, volume))
        
        # # 일별 검색량 crawling
        # print('Try except')
        try:
            volume = self.driver.find_element_by_xpath('//*[@id="appbar"]').text
            # print(volume)
            volume = volume[:volume.index('개')]
            # print(volume)
            volume = re.sub(r'[^0-9]', '', volume)
            volume = int(volume)
            print("%s's Search Volume is %d"%(date, volume))
        except:
            print('No search Volume!')
            volume = 0
            
        # crawling date update
        save_date = self.save_format_date(year, month, day)
        print('---Total result---')
        print('date: ', save_date)
        print('Volume: ', volume)
        crawl_dict = {"date":save_date, "search_volume":volume}
        self.daily_search_volume = self.daily_search_volume.append(crawl_dict, ignore_index=True)
       

       # 날짜 조회 초기화
        '''
        self.driver.find_element_by_xpath('//*[@id="hdtb-tls"]').click()
        self.driver.find_element_by_xpath('//*[@id="hdtbMenus"]/span[3]').send_keys(Keys.ENTER)
        self.driver.implicitly_wait(3)
        '''
       
        # crawling data csv 파일로 저장  
        news_df = pd.DataFrame(self.daily_search_volume)
        news_df.to_csv(keyword + "_daily_search_volume_data.csv", index = False, header = True)

        time.sleep(5)
        self.driver.back()
        self.driver.implicitly_wait(3)


    
if __name__ == "__main__":
    '''
    Crawling class 실행
    '''

    # crawling class 선언
    crawl = DailySearchVolume()
    
    # keyword 검색
    '''
    추후에 keyword가 담겨있는 파일을 열어 Keyword 하나씩 받아오는 형식으로 진행
    '''
    keyword = 'NCSOFT'
    crawl.enter_keyword(keyword)

    # keyword 일별 검색량 crawling
    crawl.search_volume_crawling(keyword)


# volume = '검색결과 약 611개 (0.48초) '
# # print(volume[7:])
# volume = volume.replace("검색결과 약 ", '')
# print(volume.index('개'))
# volume = volume[:volume.index('개')]

# print(volume)