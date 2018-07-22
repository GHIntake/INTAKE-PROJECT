from konlpy.tag import Mecab
import pandas as pd

import re
import sys
import pymssql
import pandas.io.sql as pdsql

from collections import Counter
from pprint import pprint
import pandas as pd

def frequency(merged):
    word_count = Counter(merged)
    word_count2 = []
    for i in word_count:
        word_count2.append((i, word_count[i]))
    word_count2 = sorted(word_count2, key=lambda x: x[1], reverse=True)
    return word_count2

class Social_analysis():
    syn_dic = {}
    del_list = []
    ngram_dic = {}

    def __init__(self):
        self.mecab = Mecab()
        try:
            self.load_dictionary()
        except:
            print('dictionary error')

    def load_dictionary(self, path='c:\\Users\\leeyo\\Desktop\\custom_dic.csv'):
        dic_df = pd.read_csv(path, encoding='cp949')
        for i in range(len(dic_df)):
            self.ngram_dic[dic_df.loc[i, 'key']] = dic_df.loc[i, 'value']

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

    def DB_to_table(self, query="", DBname='intake'):
        conn = pymssql.connect("intakedb.c63elkxbiwfc.us-east-2.rds.amazonaws.com:1433", "gh", "ghintake", DBname)
        self.df = pdsql.read_sql_query(query, con=conn)
        conn.close()

        self.raw_data = self.df.as_matrix()

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

    def morph_pos(self, text_list):

        morph_list = []

        for j in text_list:
            # print(j)
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

    def pos_extractor(self, parsed, exception_list=['맛', '밥', '물', '몸', '없', '있', '싫', '달', '굳', '굿', '속']):

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

        return [nav_list, noun_list, adj_list, verb_list]

    def merge_list(self, tokenized_list):
        return [j for i in tokenized_list for j in i]

    def isHangul(self, text):
        encText = text
        hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', encText))
        return hanCount > 0

intake = Social_analysis()

meals = [11200, 11306]
morning = [12100, 12115]
doctorNuts = [14101, 14102]
gonyakJelly = [14400, 14404]

# targetProduct 명시
targetProduct = morning

query = \
"""
SELECT *
FROM VproductReview 
WHERE corpName = 'KGC'
""".format(targetProduct[0], targetProduct[1])

intake.DB_to_table(query=query)

intake.morph_list = intake.morph_pos(intake.df['main_text'])
intake.nav_list, intake.noun_list, intake.adj_list, intake.verb_list = intake.pos_extractor(intake.morph_list)
intake.nav_merged = intake.merge_list(intake.nav_list)
intake.nav_frequency = frequency(intake.nav_merged)

pprint(intake.nav_frequency)

