from selenium import webdriver
import pandas as pd
import pickle as pkl
from selenium.webdriver.common.keys import Keys # 스크롤을 내리기 위해 Import


# 가상 브라우저 사용
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--diable-dev-shm-usage")
options.add_argument("user-agent={Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36}")

driver = webdriver.Chrome('/Users/eesun/Downloads/chromedriver', options = options)
driver.implicitly_wait(1)
driver.maximize_window()

# 네이버 금융 사이트
driver.get("https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=101&sid2=259")
driver.implicitly_wait(1)

## ActionChains 생성
action = webdriver.ActionChains(driver)

# 전체 뉴스 crawling data를 저장할 List
total_news_list =[]
# 각각 뉴스 crawling data를 저장하는 list
individual_news = []
# question counter
ul_counter = 1 # 1, 2 존재
li_counter = 1 # 1-10까지 존재
# 가져올 페이지 수
num_page = 10
# page counter
page_counter = 1

# page click xpath
def updateNewsPageXPath(cur_ul_counter, cur_li_counter):
    return '//*[@id="main_content"]/div[2]/ul['+str(cur_ul_counter)+']/li['+str(cur_li_counter)+']/dl/dt/a'

# question counter xpath base string
def updatePageXPath(cur_a_counter):
    return '//*[@id="main_content"]/div[3]/a['+str(cur_a_counter)+']'

# crawling 대상 - 작성 날짜 / 제목 / 본문 내용
## 작성 날짜 - #main_content > div.article_header > div.article_info > div > span
## 제목 - #articleTitle
## 본문 내용 - #articleBodyContents

while page_counter <= num_page:

    # news page click
    driver.find_element_by_xpath(updateNewsPageXPath(ul_counter, li_counter)).click()

    # 개별 뉴스 list 초기화
    individual_news = []

    # 뉴스 작성 날짜 추가
    individual_news.append([driver.find_element_by_css_selector('#main_content > div.article_header > div.article_info > div > span').text])
    driver.implicitly_wait(3)
    # 뉴스 제목 추가
    individual_news.append([driver.find_element_by_css_selector('#articleTitle').text])
    driver.implicitly_wait(3)
    # 뉴스 본문 내용 추가
    individual_news.append([driver.find_element_by_css_selector('#articleBodyContents').text])
    driver.implicitly_wait(3)

    # 개별 뉴스를 전체 뉴스 list에 추가
    total_news_list.append(individual_news)
    # 뒷 페이지로 가기
    driver.back() 
    print(ul_counter, li_counter, individual_news)
    li_counter += 1
    
    
    if ul_counter == 1 and li_counter == 11:
        li_counter = 1
        ul_counter += 1

    # 다음 장으로 넘김
    if ul_counter == 2 and li_counter == 11:
        ul_counter = 1
        li_counter = 1
        if (page_counter != 10):
            driver.find_element_by_xpath(updatePageXPath(page_counter)).click()
        page_counter += 1

    driver.implicitly_wait(3)

# crawling data를 dataframe으로 저장 & csv로 내보내기
news_df = pd.DataFrame(total_news_list)
news_df.columns = ["date", "title", "content"]
news_df.to_csv("FINANCE_news_data.csv", index=False, header=True)

print(news_df)

driver.close()