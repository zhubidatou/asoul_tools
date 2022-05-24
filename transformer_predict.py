import tensorflow as tf
import pandas as pd
import numpy as np
import re
from tensorflow import keras
from tensorflow.keras import layers
import jieba

class MultiHeadSelfAttention(layers.Layer):
    def __init__(self, embed_dim, num_heads=8):
        super(MultiHeadSelfAttention, self).__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        if embed_dim % num_heads != 0:
            raise ValueError(
                f"embedding dimension = {embed_dim} should be divisible by number of heads = {num_heads}"
            )
        self.projection_dim = embed_dim // num_heads
        self.query_dense = layers.Dense(embed_dim)
        self.key_dense = layers.Dense(embed_dim)
        self.value_dense = layers.Dense(embed_dim)
        self.combine_heads = layers.Dense(embed_dim)

    def get_config(self):  # 在有自定义网络层时，需要保存模型时，重写get_config函数
        config = {"embed_dim": self.embed_dim, "num_heads": self.num_heads, "projection_dim": self.projection_dim,
                  "query_dense": self.query_dense, "value_dense": self.value_dense, "combine_heads": self.combine_heads}
        base_config = super(MultiHeadSelfAttention, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

    def attention(self, query, key, value):
        score = tf.matmul(query, key, transpose_b=True)
        dim_key = tf.cast(tf.shape(key)[-1], tf.float32)
        scaled_score = score / tf.math.sqrt(dim_key)
        weights = tf.nn.softmax(scaled_score, axis=-1)
        output = tf.matmul(weights, value)
        return output, weights

    def separate_heads(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.projection_dim))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def call(self, inputs):
        # x.shape = [batch_size, seq_len, embedding_dim]
        batch_size = tf.shape(inputs)[0]
        query = self.query_dense(inputs)  # (batch_size, seq_len, embed_dim)
        key = self.key_dense(inputs)  # (batch_size, seq_len, embed_dim)
        value = self.value_dense(inputs)  # (batch_size, seq_len, embed_dim)
        query = self.separate_heads(
            query, batch_size
        )  # (batch_size, num_heads, seq_len, projection_dim)
        key = self.separate_heads(
            key, batch_size
        )  # (batch_size, num_heads, seq_len, projection_dim)
        value = self.separate_heads(
            value, batch_size
        )  # (batch_size, num_heads, seq_len, projection_dim)
        attention, weights = self.attention(query, key, value)
        attention = tf.transpose(
            attention, perm=[0, 2, 1, 3]
        )  # (batch_size, seq_len, num_heads, projection_dim)
        concat_attention = tf.reshape(
            attention, (batch_size, -1, self.embed_dim)
        )  # (batch_size, seq_len, embed_dim)
        output = self.combine_heads(
            concat_attention
        )  # (batch_size, seq_len, embed_dim)
        return output


'''Transformer的Encoder部分'''


class TransformerBlock(layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = MultiHeadSelfAttention(embed_dim, num_heads)
        self.ffn = keras.Sequential(
            [layers.Dense(ff_dim, activation="relu"), layers.Dense(embed_dim), ]
        )
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(rate)
        self.dropout2 = layers.Dropout(rate)

    def get_config(self):  # 在有自定义网络层时，需要保存模型时，重写get_config函数
        config = {"att": self.att, 'ffn': self.ffn, 'layernorm1': self.layernorm1, 'layernorm2': self.layernorm2,
                  'dropout1': self.dropout1,
                  'dropout2': self.dropout2}
        base_config = super(TransformerBlock, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, inputs, training):
        attn_output = self.att(inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


'''Transformer输入的编码层'''


class TokenAndPositionEmbedding(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.pos_emb = layers.Embedding(input_dim=maxlen, output_dim=embed_dim)

    def get_config(self):  # 在有自定义网络层时，需要保存模型时，重写get_config函数
        config = {"token_emb": self.token_emb, 'pos_emb': self.pos_emb}
        base_config = super(TokenAndPositionEmbedding, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x + positions

def clean_text(text):
    stopwords = pd.read_table("static/cn_stopwords.txt", header=None)
    stopwords = [word for word in stopwords[0]]
    words = re.sub("[=《》!/.,'。，、！ “’ ：·😄 ）（/\r\n, ]",'',text)
    words = jieba.lcut(words)
    words = [word for word in words if word not in stopwords]
    return words

def word_2_vec(text):
    list = []
    for word in text:
        if (word_index.get(word)) != None:
            list.append(word_index.get(word))
        else:
            list.append(0)
    return list

def create_model(MAX_LENGTH,vocab_size,embed_dim):
    inputs = layers.Input(shape=(MAX_LENGTH,))
    embedding_layer = TokenAndPositionEmbedding(MAX_LENGTH, vocab_size, embed_dim)
    x = embedding_layer(inputs)
    ff_dim = embed_dim
    transformer_block = TransformerBlock(embed_dim, 8, ff_dim)
    x = transformer_block(x)
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(20, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    outputs = layers.Dense(2, activation="sigmoid")(x)
    model = keras.Model(inputs=inputs, outputs=outputs)
    return model

def transformer_predict(str):
    text = str
    str = clean_text(str)
    MAX_LENGTH = pd.read_excel(r"static/transformer_danmu_LENGTH.xlsx")
    MAX_LENGTH = int(MAX_LENGTH[0])
    word_list = pd.read_excel(r"static/transformer_danmu.xlsx")[0]
    word_list = list(word_list)
    model = create_model(MAX_LENGTH,len(word_list),MAX_LENGTH)
    model.load_weights(r'static/mycheckpoint')
    word_index = {word_list[i]: i + 1 for i in range(len(word_list))}
    l = []
    for word in str:
        if (word_index.get(word)) != None:
            l.append(word_index.get(word))
        else:
            l.append(0)
    l = tf.keras.preprocessing.sequence.pad_sequences([l],maxlen=MAX_LENGTH)
    score = model.predict(l)
    score = np.squeeze(score)
    if score[0] > score[1]:
        return "弹幕'{}'不是逆天弹幕，该弹幕为逆天弹幕的可能性为{}%".format(text, round(score[1] * 100, 2))
    else:
        return "弹幕'{}'是逆天弹幕，该弹幕为逆天弹幕的可能性为{}%".format(text, round(score[1] * 100, 2))
