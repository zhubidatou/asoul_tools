import random
def medic():
    list_ = ['你被强化了', '，', '快上', '他会', '到欧内的手', '比较汗', '然后提升', '你的么么哒', '为了米诺和冰', '@GODIVA歌帝梵 ', '配戴着', '全套',
             '奥利安费', '@铂金Platinum ', '随手拿', '诶乌兹', '@碧欧泉Biotherm ', '欧内的赴', '@MONTBLANC万宝龙 ', '踩着', '奥克苏恩',
             '@CONVERSE中国 ', '在你的', '哈比', '下里', '@FENDI ', '凯南开的', '大@GUCCI ']
    return "".join(random.sample(list_, random.randint(15, 20))) + '#阳光信用#'