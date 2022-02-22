import pandas as pd
from konlpy.tag import Mecab
import numpy as np
from collections import Counter # 단어 빈도수를 세기 위한 모듈



##-- data load --##
news = pd.read_csv('News_Crawling/ES/[엔씨소프트]news_data.csv')
# price = pd.read_csv('News_Crawling/ES/[엔씨소프트] price_labeling.csv')

print('News data info')
print(news.info())


##-- columns of data set --##
data1 = news.columns
news.columns = ['Date', 'Title', 'Content']
news.loc[news.shape[0]] = data1

print('Changed News Data info')
print(news.info())


def remove_keyword(content):
    keyword = '엔씨소프트'
    return content.replace(keyword, "")

print(news.head())

##-- extract content --##
# contents = news.loc[:, 'Content']
# print(contents)

##-- remove keyword --##
news['Content'] = news['Content'].apply(remove_keyword)
print(news.head())

def extract_NV(word):
    if word[1][0] == 'N' or word[1][0] == 'V':
        return word

def build_word(content):
    mecab= Mecab()
    words = pd.Series(mecab.pos(content))
    word_list = []
    word_list.append(words.apply(extract_NV))
    return word_list
    

##-- emotion analysis --##
mecab  = Mecab()
word_list = []
for idx in range(len(news['Content'])):
    mecab_tag = mecab.pos(news['Content'][idx])
    for tagg in mecab_tag:
        if (tagg[1][0] == 'N' or tagg[1][0] == 'V') and (len(tagg[0]) != 1):
            word_list.append(tagg[0])
# print(word_list)


##-- frequency of words --##
# 각 단어의 빈도수를 내림차순으로 저장
emotion_dic = Counter(word_list).most_common()
print(emotion_dic)


##-- The number of unique words --##
print(len(np.unique(word_list)))

# news['Word'] = news['Content'].apply(build_word)
# print(news['Word'].head())


