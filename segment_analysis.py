import numpy as np
import pandas as pd
import tensorflow as tf
import re
import jieba

def clean_text(text):
    stopwords = pd.read_table("static/cn_stopwords.txt", header=None)
    stopwords = [word for word in stopwords[0]]
    words = re.sub("[=《》!/.,。，、！ “’ ：·😄 ）（/\r\n, ]",'',text)
    words = jieba.lcut(words)
    words = [word for word in words if word not in stopwords]
    return words


def predict(t):
    text = clean_text(t)
    model = tf.keras.models.load_model("static/danmu.h5")
    MAX_LENGTH = pd.read_excel("static/danmu_LENGTH.xlsx")
    MAX_LENGTH = int(MAX_LENGTH[0])
    word_list = pd.read_excel("static/danmu_list.xlsx")[0]
    word_list = list(word_list)
    word_index = {word_list[i]: i + 1 for i in range(len(word_list))}
    l = []
    for word in text:
        if (word_index.get(word)) != None:
            l.append(word_index.get(word))
        else:
            l.append(0)
    text = [l]
    text = tf.keras.preprocessing.sequence.pad_sequences(text, maxlen=MAX_LENGTH)
    score = model.predict(text)
    score = np.squeeze(score)
    if score[0] > score[1]:
        return 0
    else:
        return 1

def danmu_preprocess(data):
    data.dropna(inplace=True)
    time = [text.split("*")[0] for text in data['0']]
    username = [text.split("*")[1] for text in data['0']]
    content = [text.split("*")[2] for text in data['0']]
    data['time'] = time
    data['username'] = username
    data['content'] = content
    data = data[['time','username','content']]
    return data

data = pd.read_excel('h://521.xlsx')
data = data[['word','count']]
word_list = data['word']
count_list = data['count']
predict_result = []
for text in word_list:
    if predict(text) == 1:
        predict_result.append(1)
    else:
        predict_result.append(0)
result = pd.DataFrame()
result['评论'] = word_list
result['词频'] = count_list
result['逆天弹幕'] = predict_result
result.to_csv("/static/521逆天弹幕统计.csv")