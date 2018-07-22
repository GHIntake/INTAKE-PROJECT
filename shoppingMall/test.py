from konlpy.tag import Mecab
import pickle
import re
import sys
from gensim.models import TfidfModel
from gensim.models import Word2Vec
from gensim.corpora import Dictionary
from pprint import pprint
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import mglearn
from pprint import pprint
import numpy as np
import gc
import copy
import pandas as pd


class SB_Word2Vec():

    def __init__(self, morph_list):
        self.dct = Dictionary(morph_list)
        self.corpus = [self.dct.doc2bow(line) for line in morph_list]
        self.build_Word2Vec(morph_list)

    def make_Word2Vec(self, morph_list, size=50, window=2, min_count=10, iteration=100):
        self.em = Word2Vec(morph_list, size=size, window=window, min_count=min_count, iter=iteration)
        self.em_vocab = list(self.em.wv.vocab.keys())
        self.em_vocab_dic = {word: idx for idx, word in enumerate(self.em_vocab)}

    def make_Word2Sen_matrix(self):
        vocab_size = len(self.em_vocab)
        self.sen_matrix = np.zeros((len(self.corpus), vocab_size))
        for idx, row in enumerate(self.sen_matrix):
            for idx2, frequency in self.corpus[idx]:
                if self.dct[idx2] in self.em_vocab:
                    self.sen_matrix[idx][self.em_vocab_dic[self.dct[idx2]]] = frequency
        self.sim_matrix = np.zeros((vocab_size, vocab_size))
        for idx, w1 in enumerate(self.em_vocab):
            for idx2, w2 in enumerate(self.em_vocab):
                self.sim_matrix[idx][idx2] = self.em.wv.similarity(w1, w2)

        self.word2sen_matrix = np.dot(self.sim_matrix, np.transpose(self.sen_matrix))

        return self.word2sen_matrix

    def get_sim_sen(self, keyword, main_text, number=1):
        self.sim_sen_index = np.argsort(self.word2sen_matrix[self.em_vocab_dic[keyword]])
        self.most_sim_sen_index = np.argmax(self.word2sen_matrix[self.em_vocab_dic[keyword]])
        index_list = self.sim_sen_index.reshape((-1,)).tolist()
        index_list.reverse()

        for idx, i in enumerate(index_list[:number]):
            print(str(idx + 1))
            print(main_text[i])
        return index_list

    def build_Word2Vec(self, morph_list):
        self.make_Word2Vec(morph_list)
        self.make_Word2Sen_matrix()


class SB_LDA():

    def make_lda(self, morph_joined, ntopic=10, learning_method='batch', max_iter=25, random_state=0, n_words=20):
        self.vect = CountVectorizer(max_features=10000, max_df=.15)
        self.X = self.vect.fit_transform(morph_joined)
        self.lda = LatentDirichletAllocation(n_components=ntopic, learning_method=learning_method, max_iter=max_iter,
                                             random_state=random_state)
        self.document_topics = self.lda.fit_transform(self.X)
        self.sorting = np.argsort(self.lda.components_, axis=1)[:, ::-1]
        self.feature_names = np.array(self.vect.get_feature_names())
        mglearn.tools.print_topics(topics=range(ntopic), feature_names=self.feature_names, sorting=self.sorting,
                                   topics_per_chunk=5, n_words=n_words)

    def related_doc(self, main_text_list, topic_index, number=10):
        category = np.argsort(self.document_topics[:, topic_index])[::-1]
        related_docs = []
        for i in category[:number]:
            print(i)
            print(main_text_list[i] + ".\n")
            related_docs.append((i, main_text_list[i]))
        return related_docs


class SB_Tfidf():

    def __init__(self, list_morph_merged):
        self.list_morph_merged = list_morph_merged
        self.dct = Dictionary(self.list_morph_merged)
        self.corpus = [self.dct.doc2bow(line) for line in self.list_morph_merged]

    def get_tfidf(self):
        self.model = TfidfModel(self.corpus)
        self.tfidf = []
        for i in self.corpus:
            self.tfidf.append(sorted(self.model[i], key=lambda x: x[1], reverse=True))
        self.tfidf_hangul = []
        for idx1, i in enumerate(self.tfidf):
            self.tfidf_hangul.append([(self.dct[j[0]], j[1]) for j in i])

        return self.tfidf_hangul


def frequency(merged):
    word_count = Counter(merged)
    word_count2 = []
    for i in word_count:
        word_count2.append((i, word_count[i]))
    word_count2 = sorted(word_count2, key=lambda x: x[1], reverse=True)
    return word_count2


class Social_analysis():
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    syn_dic = {}
    del_list = []
    ngram_dic = {}

    def __init__(self):
        self.mecab = Mecab()
        try:
            self.load_dictionary()
        except:
            print('dictionary error')

    def load_dictionary(self, path='Data/custom_dic.csv'):
        dic_df = pd.read_csv(path, encoding='cp949')
        for i in range(len(dic_df)):
            self.ngram_dic[dic_df.loc[i, 'key']] = dic_df.loc[i, 'value']

    def DB_to_table(self, DBname='intake', keyword='intake'):
        import pymssql
        import pandas.io.sql as pdsql
        import pandas as pd
        self.query = \
            """
            SELECT user_id, created_at, main_text, hashtags, comments, likes, current_url FROM instaPosting WHERE keyword = '{}'
            """.format(keyword)
        conn = pymssql.connect("intakedb.c63elkxbiwfc.us-east-2.rds.amazonaws.com:1433", "gh", "ghintake", DBname)
        self.df = pdsql.read_sql_query(self.query, con=conn)
        # df['main_text'] = df.main_text.apply(lambda x: x.replace('#',' ').translate(self.non_bmp_map))
        # df['created_at'] = df.created_at.apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        conn.close()
        self.raw_data = self.df.as_matrix()

    def pickle_to_table(self, filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        data = data[1:]
        for idx, i in enumerate(data):
            data[idx][2] = i[2].replace('#', ' ').translate(self.non_bmp_map)
            data[idx][3] = '/'.join(i[3])
            data[idx][4] = '/'.join(i[4])
        self.raw_data = np.array(data)

    def hashtags_split(self, hashtags):
        hashtags_split = []
        for i in hashtags:
            hashtags_split.append(i.split('/'))

        hashtags_list = []

        for i in hashtags_split:
            temp = []
            for j in i:
                if self.isHangul(j):
                    t_hashtags = j.translate(self.non_bmp_map)
                    temp.append(t_hashtags)
            hashtags_list.append(temp)
        self.hashtags_list = hashtags_list

        return hashtags_list

    def add_dictionary(self, *tokenized_list):
        origin_df = 1
        try:
            origin_df = pd.read_csv("C:\\mecab\\user-dic\\intake_dic.csv", encoding='utf-8', header=None)
        except:
            print('No default intake_dic')
        keyword_list = []
        for i in tokenized_list:
            if type(i) == list:
                for j in i:
                    j = j.split('_')
                    temp = [j[0], '', '', '', j[1], '*', j[2], j[3], '*', '*', '*', '*', '*']
                    keyword_list.append(temp)
            else:
                i = i.split('_')
                temp = [i[0], '', '', '', i[1], '*', i[2], i[3], '*', '*', '*', '*', '*']
                keyword_list.append(temp)

        keyword_df = pd.DataFrame(keyword_list)
        print(type(origin_df))
        if type(origin_df) != int:
            keyword_df = pd.concat((origin_df, keyword_df), ignore_index=True)
        else:
            print('a')
            pass
        print(keyword_df.shape)

        keyword_df.to_csv("C:\\mecab\\user-dic\\intake_dic.csv", encoding='utf-8', index=None, header=False)

    def ngram(self, parsed_list):

        ngram_list = []
        adjustment = 0
        for idx in range(len(parsed_list)):
            idx = idx + adjustment
            n_filter = '/'.join(parsed_list[idx:idx + self.ngram_size])
            if n_filter in self.ngram_dic:
                ngram_list.append(self.ngram_dic[n_filter])
                adjustment += (self.ngram_size - 1)
            else:
                ngram_list.append(n_filter.split('/')[0])

        if self.ngram_size == 2:
            return ngram_list
        else:
            self.ngram_size -= 1
            return self.ngram(ngram_list)

    def morph_pos(self, text_list):

        morph_list = []

        for j in text_list:
            parsed = self.mecab.pos(j)
            temp = []
            for i in parsed:
                if self.isHangul(i[0]):
                    temp.append(i[0] + '_' + i[1])
                else:
                    pass  # print('{} 한글이 아님.'.format(i[0]))

            self.ngram_size = 5
            morph_list.append(self.ngram(temp))

        self.df['morph_list'] = morph_list
        return morph_list

    def filter_words(self, parsed_list):
        # 1차원 리스트를 받음.
        changed_list = list(map(lambda x: self.syn_dic.get(x, x), parsed_list))
        deleted_list = list(filter(lambda x: x not in self.del_list, changed_list))
        return deleted_list

    def pos_extractor(self, parsed, exception_list=['맛', '밥', '물', '몸', '죽', '먹', '없', '있', '싫', '헬', '달']):

        noun_list = []
        adj_list = []
        verb_list = []
        nav_list = []
        for j in parsed:

            nav_temp = []
            n_temp = []
            adj_temp = []
            verb_temp = []

            for i in j:
                i = i.split('_')
                if self.isHangul(i[0]):
                    if (len(i[0]) > 1) or (i[0] in exception_list):
                        if 'NN' in i[1]:
                            n_temp.append(i[0])
                            nav_temp.append(i[0])
                        elif 'VV' in i[1]:
                            adj_temp.append(i[0])
                            nav_temp.append(i[0])
                        elif 'VA' in i[1]:
                            verb_temp.append(i[0])
                            nav_temp.append(i[0])
                    else:
                        pass
                    # print('{} 제외'.format(i[0]))
                else:
                    pass  # print('{} 한글이 아님.'.format(i[0]))

            nav_list.append(self.filter_words(nav_temp))
            noun_list.append(self.filter_words(n_temp))
            adj_list.append(self.filter_words(adj_temp))
            verb_list.append(self.filter_words(verb_temp))

        columns = ['nav_list', 'noun_list', 'adj_list', 'verb_list']
        for i in zip(columns, [nav_list, noun_list, adj_list, verb_list]):
            self.df[i[0]] = i[1]

        return [nav_list, noun_list, adj_list,
                verb_list]  # tuple(map(lambda x: [j.split('_')[0] for j in x], [nav_list, noun_list, adj_list, verb_list]))

    def merge_list(self, tokenized_list):
        return [j for i in tokenized_list for j in i]

    def join_list(self, tokenized_list):
        joined_list = []
        for idx, i in enumerate(tokenized_list):
            joined_list.append(" ".join(i))
        return joined_list

    def split_list(self, untokenized_list):
        hashtag_splited = []
        for idx, i in enumerate(untokenized):
            hashtag_splited.append(i.split('/'))
            return hastag_splited

    '''    
    def join_underbar(self, morph_list):

        all_list = []
        post_list=[]
        for i in morph_list:
            for j in i:
                post_list.append(j[0]+'_'+j[1])
            all_list.append([(' , ').join(post_list)])
            post_list=[] 
        all_list=np.array(all_list)

        return all_list'''

    def word_substitute(self, dataset, sublist):
        dataset = copy.deepcopy(dataset)
        sub_book = dict()
        for i in sublist:
            for j in i['sub_words']:
                sub_book[j] = i['main']
        gc.collect()
        for n, i in enumerate(dataset):
            dataset[n] = [sub_book.get(item, item) for item in i]

        del sub_book
        gc.collect()

        return dataset

    def word_delete(self, dataset, del_list):
        dataset = copy.deepcopy(dataset)

        for n, line in enumerate(dataset):
            dataset[n] = [i for i in line if i not in del_list]

        return dataset

    def isHangul(self, text):
        encText = text
        hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', encText))
        return hanCount > 0

    def convert_list(self, *tokenized_list):
        input_length = len(tokenized_list)
        lists = [[] for i in range(input_length)]

        for idx, li in enumerate(tokenized_list):
            for j in li:
                lists[idx].append(['/'.join(j)])

        converted_array = np.array(lists[0])
        for idx in range(input_length):
            try:
                converted_array = np.concatenate((converted_array, lists[idx + 1]), axis=1)
            except Exception as e:
                print(e, '끝')

        return converted_array

    def make_df(self, start_array, converted_array, end_array,
                columns=['user_id', 'created_at', 'main_text', 'morph_list', 'nav_list', 'noun_list', 'adj_list',
                         'verb_list', 'hashtags', 'comments', 'likes', 'current_url']):
        df = pd.DataFrame(np.hstack((start_array, converted_array, end_array)), index=None, columns=columns)
        return df

    # 키워드 리스트 중 하나라도 있는 경우
    def word_check_or(self, text, keywords):
        if any(word in text for word in keywords):
            return 1
        else:
            return 0

    # 키워드 리스트에 있는 단어가 모두 있는 경우
    def word_check_and(self, text, keywords):
        if all(word in text for word in keywords):
            return 1
        else:
            return 0

    def word_check(self, method, keywords, df, column_name='main_text', filter_TF=True):

        filter_TF = 1 if filter_TF == True else 0
        if method == 'and':
            df['flags'] = df[column_name].apply(lambda x: self.word_check_and(x, keywords))
            return df.loc[df['flags'] == filter_TF]

        elif method == 'or':
            df['flags'] = df[column_name].apply(lambda x: self.word_check_or(x, keywords))
            return df.loc[df['flags'] == filter_TF]

        else:
            print('Select method, and/or')