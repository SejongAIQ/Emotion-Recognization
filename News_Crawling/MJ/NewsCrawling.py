# For BeautifulSoup
from bs4 import BeautifulSoup

# For Selenium
from selenium import webdriver

# Selenium_driver -> Safari 사용
driver = webdriver.Safari()

# 접속할 url
# {'에스디바이오센서': 137310} #'https://finance.naver.com/item/news_news.naver?code={Code_num}'
# 뒤에 Code_num 부분을 수정하면 다른 기업의 뉴스 목록 가져올 수 있음
url = 'https://finance.naver.com/item/news_news.naver?code=137310'
driver.get(url)
page_html = driver.page_source

# BeautifulSoup로 page Html 파싱
soup = BeautifulSoup(page_html, 'html.parser')

# html 속 title 덩어
body = soup.select_one('tbody')
# title이 들어간 a태그 리스트 추출
news_list = body.select('tr > td.title > a')
news_link_list = {}

for news in news_list:
    title, href = news.string, news.attrs['href']
    news_link_list[title] = href

url_pre = 'https://finance.naver.com'

for title, link in news_link_list.items():
    news_url = url_pre + link  # news 별 url
    driver.get(news_url)
    page_html = driver.page_source

    soup = BeautifulSoup(page_html, 'html.parser')
    body = soup.select_one('table.view')

    contents = body.select('tr > td > div#news_read').get_text() # 본문 내용
    date = body.find("span", class_="p11").get_text() # 날짜

    print(contents)
    break
