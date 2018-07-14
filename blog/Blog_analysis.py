from ckonlpy.tag import Twitter
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
from ckonlpy.tag import Twitter
import numpy as np
import gc
import copy

class Social_analysis():
    
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

    def __init__(self):
        self.twitter = Twitter()
        
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
                    
    def add_keyword_dic(self, keyword_list, tag='Noun'):
        for i in keyword_list:
            if type(i) == tuple:
                self.twitter.add_dictionary(i[0], i[1])
            else:
                self.twitter.add_dictionary(i, tag)
        
    def morph_pos(self, text_list, exception_list = ['맛', '밥', '물', '몸']):
        
        morph_list = []
        noun_list = []
        adj_list = []
        verb_list = []
        
        for j in text_list:
            parsed = self.twitter.pos(j)
            temp = []
            n_temp = []
            adj_temp = []
            verb_temp = []
            
            for i in parsed:
                if self.isHangul(i[0]):
                    if ((len(i[0]) > 1) or (i[0] in exception_list)):
                        temp.append(i)
                        if i[1] == 'Noun':
                            n_temp.append(i[0])
                        elif i[1] == 'Verb':
                            adj_temp.append(i[0])
                        elif i[1] == 'Adjective':
                            verb_temp.append(i[0])
                    else:
                        print('{} 제외'.format(i[0]))
                else: print('{} 한글이 아님.'.format(i[0]))
            

            morph_list.append(temp)
            noun_list.append(n_temp)
            adj_list.append(adj_temp)
            verb_list.append(verb_temp)

        nav_list = noun_list + adj_list + verb_list

        return morph_list, nav_list, noun_list, adj_list, verb_list

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

    def word_substitute(self, dataset, sublist):
        dataset = copy.deepcopy(dataset)
        sub_book = dict()
        for i in sublist:
            for j in i['sub_words']:
                sub_book[j] = i['main']
        gc.collect()
        for n, i in enumerate(dataset):
            dataset[n] = [sub_book.get(item,item) for item in i]

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

    

class SB_Word2Vec():    
    
    def __init__(self, morph_list):
        self.dct = Dictionary(morph_list)
        self.corpus = [self.dct.doc2bow(line) for line in morph_list]
        self.build_Word2Vec(morph_list)
    
    def make_Word2Vec(self, morph_list, size=50, window=2, min_count=10, iteration=100):
        self.em = Word2Vec(morph_list, size=size, window=window, min_count=min_count, iter=iteration)
        self.em_vocab = list(self.em.wv.vocab.keys())
        self.em_vocab_dic = {word:idx for idx, word in enumerate(self.em_vocab)}

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
                self.sim_matrix[idx][idx2] =  self.em.wv.similarity(w1, w2)

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
        self.lda = LatentDirichletAllocation(n_components=ntopic, learning_method=learning_method, max_iter=max_iter, random_state=random_state)
        self.document_topics = self.lda.fit_transform(self.X)
        self.sorting = np.argsort(self.lda.components_, axis=1)[:, ::-1]
        self.feature_names = np.array(self.vect.get_feature_names())
        mglearn.tools.print_topics(topics=range(ntopic), feature_names=self.feature_names, sorting=self.sorting, topics_per_chunk=5, n_words=n_words)

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
             self.tfidf.append(sorted(self.model[i], key = lambda x: x[1], reverse=True))
        self.tfidf_hangul = []
        for idx1, i in enumerate(self.tfidf):
            self.tfidf_hangul.append([(self.dct[j[0]], j[1]) for j in i])        
        
        return self.tfidf_hangul
    
def frequency(merged):
    word_count = Counter(merged)
    word_count2 = []
    for i in word_count:
        word_count2.append((i, word_count[i]))
    word_count2 = sorted(word_count2, key=lambda x: x[1], reverse = True)
    return word_count2
