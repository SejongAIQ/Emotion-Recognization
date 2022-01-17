# Module import

from operator import index
from bs4 import BeautifulSoup # For BeautifulSoup
import pandas as pd # For DB
from selenium import webdriver # For Selenium
import re # For data cleaning 
import warnings
import time

warnings.filterwarnings('ignore')

# 접속할 url
# {'에스디바이오센서': 137310} #'https://finance.naver.com/item/news_news.naver?code={Code_num}'
# 뒤에 Code_num 부분을 수정하면 다른 기업의 뉴스 목록 가져올 수 있음

class News : 
    
    # 초기화 함수 
    def __init__(self): 
        self.driver = webdriver.Safari() # safari driver 생성
        self.url_pre = 'https://finance.naver.com'

    # 소멸자 함수
    def __del__(self):
        self.driver.close()

    # 문자열 cleaning 함수 
    def string_cleaning(self, string):
        result = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]',' ', string)
        result = ' '.join(result.split()).rstrip()
        return result

    # page_bar에서 마지막 페이지 찾는 함수 
    # 시세에서는 사용가능하지만 뉴스에서는 맨 뒤를 눌러도 마지막 url로 가지 않기 때문에 수정 완료
    def find_lastpage(self, pages): 

        while self.string_cleaning(pages[-1].text) == '맨뒤':
            
            pages[-1].click()

            try:
                page_bar = self.driver.find_element_by_class_name('navi')
                pages = page_bar.find_elements_by_css_selector('a')
            except:
                page_bar = self.driver.find_element_by_class_name('Nnavi')
                pages = page_bar.find_elements_by_css_selector('a')
            
        number = re.findall(r'\d+', self.driver.current_url)

        return int(number[-1])

    # page별로 url 가져오기 
    def news_content_crawling(self, code):
        self.url = f'https://finance.naver.com/item/news_news.naver?code={code}' #url 설정
        self.driver.get(self.url) # 해당 페이지 loading

        news_crawling = pd.DataFrame(columns={'title', 'date', 'contents'})
        
        page_html = self.driver.page_source

        # BeautifulSoup로 page Html 파싱
        soup = BeautifulSoup(page_html, 'html.parser')

        # 마지막 페이지 찾기 위한 navi bar 찾기 
        page_bar = self.driver.find_element_by_class_name('Nnavi')
        pages = page_bar.find_elements_by_css_selector('a')
        
        # 마지막 페이지
        last_page = self.find_lastpage(pages)

        page_url = f'https://finance.naver.com/item/news_news.naver?code={code}&page='

        for page_num in range(1, last_page  + 1):
            current_page = page_url + str(page_num)
            
            self.driver.get(current_page)
            page_html = self.driver.page_source

            soup = BeautifulSoup(page_html, 'html.parser')

            # html 속 title
            body = soup.select_one('tbody')
            # title이 들어간 a태그 리스트 추출
            news_list = body.select('tr > td.title > a')
            self.news_link_list = {}

        
            for news in news_list:
                title, href = news.string, news.attrs['href'] # 제목, url
                self.news_link_list[title] = href


            for title, link in self.news_link_list.items():

                # new url로 접속해서 페이지 정보 파싱하기 
                news_url = self.url_pre + link  # news 별 url
                self.driver.get(news_url)
                page_html = self.driver.page_source

                soup = BeautifulSoup(page_html, 'html.parser')
                body = soup.select_one('table.view')

                # title 가져오기
                title = body.find("strong").get_text()

                # 본문 내용 가져오기 
                contents = body.select_one('tr > td > div#news_read') 

                # 본문 내용에서 text만 뽑아오기 
                contents_text = contents.get_text()
                
                # 본문 내용 cleaning
                contents_text_re = self.string_cleaning(contents_text)
                contents_text_re = ' '.join(contents_text_re.split())
                
                # 날짜 가져오기
                date = body.find("span", class_="p11").get_text()
                
                # DataDrame에 추가하기 
                news = {'title' : title, 'date': date, 'contents': contents_text_re}
                news_crawling = news_crawling.append(news, ignore_index=True) 

        news_crawling.to_csv('news_crawling.csv', index=None, header=True)


    def price_crawling(self, code):
        self.url = f'https://finance.naver.com/item/sise_day.naver?code={code}&page=1' #url 설정
        self.driver.get(self.url) # 해당 페이지 loading
        
        # 데이터 저장할 DF
        price_crawling = pd.DataFrame()

        # 마지막 페이지 찾기 위한 navi bar 찾기 
        page_bar = self.driver.find_element_by_class_name('Nnavi')
        pages = page_bar.find_elements_by_css_selector('a')
      
        # 마지막 page 수 받기 
        # 시세는 아마 마지막 페이지가 26(1년치)보다 크면 26으로 설정하고 아니면 last page 고정하는 방법 사용할 듯
        last_page = self.find_lastpage(pages)


        page_url = f'https://finance.naver.com/item/sise_day.naver?code={code}&page='

        # page 별로 가격 받아오기 
        for page in range(1, last_page + 1):
            current_page = page_url + str(page)
            
            self.driver.get(current_page)
            page_html = self.driver.page_source

            # html 속 날짜 + 시세 
            price_crawling = price_crawling.append(pd.read_html(page_html)[0])

        # 빈 값 제거 
        price_crawling.dropna(inplace=True)
        price_crawling.to_csv('price.csv', index=None, header= True)

        

if __name__ == "__main__":
    news = News()

    # 뉴스 크롤링
    news.news_content_crawling(137310)
    
    # 삼성전자 005930 
    # 시세 크롤링 
    news.price_crawling('137310')