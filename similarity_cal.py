import pandas as pd
import re
import jieba
import numpy as np

def clean_text(str):
    pattern = re.compile(u'['u'\U0001F300-\U0001F64F' u'\U0001F680-\U0001F6FF'u'\u2600-\u2B55]+')
    str = pattern.sub("",str)
    str = re.sub("[=《》!/.,。，、！ “’ ：·😄 <>）\u200b（a-zA-Z0-9/\r\n, ]",'',str)
    if str != "" and len(str)>3:
        return str

def simliarity_cal(str1,str2):
    vec1,vec2 = get_word_vector(str1,str2)
    return cos_dist(vec1,vec2)


def get_word_vector(s1, s2):
    # 分词
    cut1 = jieba.cut(s1)
    cut2 = jieba.cut(s2)
    list_word1 = (','.join(cut1)).split(',')
    list_word2 = (','.join(cut2)).split(',')
    # 列出所有的词,取并集
    key_word = list(set(list_word1 + list_word2))
    # 给定形状和类型的用0填充的矩阵存储向量
    word_vector1 = np.zeros(len(key_word))
    word_vector2 = np.zeros(len(key_word))
    # 计算词频
    # 依次确定向量的每个位置的值
    for i in range(len(key_word)):
        # 遍历key_word中每个词在句子中的出现次数
        for j in range(len(list_word1)):
            if key_word[i] == list_word1[j]:
                word_vector1[i] += 1
        for k in range(len(list_word2)):
            if key_word[i] == list_word2[k]:
                word_vector2[i] += 1

    return word_vector1, word_vector2

def cos_dist(vec1,vec2):
    dist1=float(np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2)))
    return dist1

def str_cal(str):
    text = pd.read_excel("static//word_dict.xlsx")
    text = text.dropna()
    text = text['comment']
    word_dict = [clean_text(line) for line in text]
    word_dict = list(filter(None, word_dict))
    max_score = 0
    sim_str = ""
    for item in word_dict:
        score = simliarity_cal(str,item)
        if score>max_score:
            max_score = score
            sim_str = item
    return "评论与语料库的相似度为{}%，最相似的句子为:{}".format(round(max_score*100),sim_str)
