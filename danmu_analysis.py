import requests
import time
import pandas as pd
import re
import jieba
from wordcloud import WordCloud
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei']
def get_msg():
    roomid = "22632424"
    url = "https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory"
    headers = {
        "Host": "api.live.bilibili.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }
    data = {
        "roomid": roomid,
    }
    html = requests.post(url=url, headers=headers, data=data).json()

    return html


def write_msg2txt(html, danmu_list):
    for content in html["data"]["room"]:
        # 获取昵称
        nickname = content["nickname"]
        # 获取发言
        text = content["text"]
        # 获取发言时间
        timeline = content["timeline"]
        # 记录发言
        msg = timeline + "*" + nickname + "*" + text
        # 不存在则添加
        # if msg not in msg_data:
        # print(msg)
        danmu_list.append(msg)
        print(msg)


def sleeptime(hour, min, sec):
    return hour * 3600 + min * 60 + sec


second = sleeptime(0, 0, 2)


def get_danmu():
    danmu_list = []
    for i in range(30):
        time.sleep(second)
        ##print("do action")
        # 5秒采集一次
        html = get_msg()
        write_msg2txt(html, danmu_list)
    data = pd.DataFrame(danmu_list)
    data.dropna(inplace=True)
    data.to_csv("static/Danmu.csv")
    data.to_csv("static/Danmu_all.csv", mode='a')


def create_wordcloud():
    data = pd.read_csv("static/Danmu.csv")
    data.drop_duplicates(keep=False,inplace=True)
    data.dropna(inplace=True)
    data.columns = ['0', '1']
    data = [text.split("*")[2] for text in data['1']]
    str = "".join(data)
    wc = WordCloud(background_color='white',font_path='/usr/local/lib/python3.8/dist-packages/matplotlib/mpl-data/fonts/ttf/SimHei.ttf',width=350,height=250,max_words=50).generate(str)
    wc.to_file("static/wc.jpg")


def clean_text(text):
    stopwords = pd.read_table("static/cn_stopwords.txt", header=None)
    stopwords = [word for word in stopwords[0]]
    words = re.sub("[=《》! /.,。，、！ ｀', '・',  'ω', '・', '´ω<“’ ：·😄 ）（a-zA-Z0-9/\r\n, ]", '', text)
    words = jieba.lcut(words)
    words = [word for word in words if word not in stopwords]
    return words


def tfidf(corpus):
    vector = TfidfVectorizer()  # 将停词引入模型,tfidf=TfidfVectorizer(token_pattern=r"(?u)\b\w\w+\b",stop_words=stopword)
    tfidf = vector.fit_transform(corpus)  # 模型向量化
    ###每次词和TF-IDF的对应关系
    word = vector.get_feature_names()  # 获取词带模型中的所有词
    weightlist = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    # 保存特征文本
    return word


def get_top10():
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

while True:
    try:
        get_danmu()
        create_wordcloud()
        get_top10()
    except:
        get_danmu()
        create_wordcloud()
        get_top10()
