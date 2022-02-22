from selenium import webdriver 
from bs4 import BeautifulSoup
import pandas as pd
import json
import time 

class Insta:
    def __init__(self):
        
        with open('./DATA/config.json','r') as in_file:
            config = json.load(in_file)
            username = config['instagram_username']
            password = config['instagram_password']

        # 자동 로그인을 위한 정보     
        self.username = username
        self.password = password

        # setting 
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("user-agent={Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36}")

        # Chrome 가상 driver 열기 
        self.driver = webdriver.Chrome('/Users/user/Downloads/chromedriver_win32/chromedriver.exe') #chromedriver 로드
        self.driver.implicitly_wait(3) # 웹 페이지 전체가 넘어올 때까지 기다리기 
        self.driver.maximize_window()  # window size 지정 (maximize)
    
    def __del__(self):
        self.driver.close()
    
    def login_insta(self):

        ## instagram 자동 로그인 ##
        self.driver.get("https://www.instagram.com")
        # username 요소에 id 전송
        element_id = self.driver.find_element_by_name("username")
        element_id.send_keys(self.username)
        # password 요소에 pw 전송
        element_password = self.driver.find_element_by_name("password")
        element_password.send_keys(self.password)
        time.sleep(2)
        # 로그인 버튼 클릭 - HTML class 값 : .sqdOP.L3NKy.y3zKF
        self.driver.find_element_by_css_selector('.sqdOP.L3NKy.y3zKF').click()
        self.driver.implicitly_wait(100)
        time.sleep(5)
        # 나중에 하기 버튼 클릭 
        self.driver.find_element_by_css_selector('.sqdOP.yWX7d.y3zKF').click()
        time.sleep(2)
        self.driver.find_element_by_css_selector('.aOOlW.HoLwm').click()
        time.sleep(2)

    def tag_searching(self):

        url = f"https://www.instagram.com/explore/tags/%EC%97%90%ED%94%84%EC%95%A4%EC%97%90%ED%94%84/" # 에프앤에프 url 
        self.driver.get(url)                                                                           # 해시태그 에프앤에프 검색 결과 html 열기 

        # 첫번째 게시물 클릭 
        first_post = self.driver.find_elements_by_css_selector('div._9AhH0')[0]
        first_post.click()
        time.sleep(3)

    def get_content_example(self):

        # 인스타그램 자동 로그인
        self.login_insta()                
        # 해시태그 검색                                           
        self.tag_searching()

        # 연결된 드라이버 html 파일 로드 
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        # content 가져오기 
        content = soup.select('div.C4VMK > span')[0].text
        print(content)

    
    ## [ 구현 예정 ] ##
    def get_tag_list(self):
        tags = pd.read_csv('tag_by_Sector')
        return tags
        
    def insta_crawling(self):

        tags = self.get_tag_list() # 태그 리스트 반환
        self.login_insta() # 인스타그램 자동 로그인               

        for i in len(tags):
            self.tag_searching()

            if i == 0 :             
                # 첫번째 게시물 클릭 
                first_post = self.driver.find_elements_by_css_selector('div._9AhH0')[0]
                first_post.click()
                time.sleep(3)    

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'lxml')

            content = soup.select('div.C4VMK > span')[0].text
            print(content)

        




if __name__ == "__main__":
    insta = Insta()
    insta.get_content_example()