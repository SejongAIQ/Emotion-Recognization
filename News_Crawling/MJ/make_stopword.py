stopword = open('./Data/korean_stopwords.txt', 'r')

def make_stopword(stopword):
    words = []

    while True:
        line = stopword.readline()
        if not line : break
        l = line.split('\t')
        words.append(l[0])
    
    return words

words = make_stopword(stopword)
