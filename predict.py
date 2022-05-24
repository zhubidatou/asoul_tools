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
        return "弹幕'{}'不是逆天弹幕，该弹幕为逆天弹幕的可能性为{}%".format(t,round(score[1]*100,2))
    else:
        return "弹幕'{}'是逆天弹幕，该弹幕为逆天弹幕的可能性为{}%".format(t,round(score[1]*100, 2))
