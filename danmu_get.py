import requests
import time
import pandas as pd
import re
import jieba
from wordcloud import WordCloud
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
def clean_text(text):
    stopwords = pd.read_table("static/cn_stopwords.txt", header=None)
    stopwords = [word for word in stopwords[0]]
    words = re.sub("[=《》! /.,。，、！ ｀', '・',  'ω', '・', '´ω<“’ ：·😄 ）（a-zA-Z0-9/\r\n, ]", '', text)
    words = jieba.lcut(words)
    words = [word for word in words if word not in stopwords]
    return words

sns.set(font='SimHei')
data = pd.read_csv("static/Danmu.csv")
data.dropna(inplace=True)
data.drop_duplicates(keep=False, inplace=True)
data.columns = ['0', '1']
data = [text.split("*")[2] for text in data['1']]
data = [clean_text(line) for line in data]
wl = []
for word in data:
    for item in word:
        wl.append(item)
word_dict = {}
for word in wl:
    if word in word_dict:
        word_dict[word] += 1
    else:
        word_dict[word] = 1
word_dict = list(word_dict.items())  # 将键值对转换成列表
word_dict.sort(key=lambda x: x[1], reverse=True)  # 根据词语出现的次数进行从大到小排序
word_list = []
count_list = []
for word, count in word_dict[:10]:
    word_list.append(word)
    count_list.append(count)
fig = sns.barplot(x=count_list, y=word_list, palette="husl")
fig.figure.set_size_inches(3.5, 3)
fig.set_title('最近2分钟弹幕中出现最频繁的10个词语')
sns.set_theme(style='whitegrid')
sns.set_color_codes("muted")
boxplot = fig.get_figure()
savepath = r"static/top10.jpg"
boxplot.savefig(savepath)
print('ok')