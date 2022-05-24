import jieba
def synonym_change(str):
    # 读取同义词表，并生成一个多维数组
    combine_array = []
    # synonyms_words.txt是同义词表，每行是一系列同义词，用空格分隔
    for line in open("static//synonyms_words.txt", "r", encoding='utf-8'):
        seperate_word = line.strip().split(" ")#将空格分隔符变为逗号
        combine_array.append(seperate_word)
    #使用jieba分词
    str1 = jieba.lcut(str)
    #同义词替换，不论位置，所以用数组存放同义词
    for i in range(len(str1)):
        for line in combine_array:
            if line[0] == str1[i]:
                str1[i] = line[1]
                continue
            if line[1] == str1[i]:
                str1[i] = line[0]
                continue
    str1 = ''.join(str1)
    return str1