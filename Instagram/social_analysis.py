
# coding: utf-8

# In[1]:


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
import data_handler as handler
import data_analyzer as analyzer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import mglearn
from pprint import pprint


class Social_analysis():    
    def __init__(self, filename, filter_id=None):
        self.data = handler.load_by_pickle(filename, filter_id)
        self.dataset, self.dataset_dic, self.main_text_list, self.morph_list, self.morph_merged, self.morph_joined, self.hashtags_merged, self.hashtags_appended, self.main_hash_dic = handler.create_datasets(self.data)
        



intake = Social_analysis('intake.txt', 'intakefoods')

labnosh = Social_analysis('labnosh.txt', 'labnosh.official')

meals = Social_analysis('meals.txt', 'intakefoods')

morningjuk = Social_analysis('morningjuk.txt', 'intakefoods')

easy_food = Social_analysis('easy_food.txt')

conven_food = Social_analysis('conven_food.txt')

keywords = [intake, labnosh, meals, morningjuk, easy_food, conven_food]

### 빈도분석

for i in keywords:
    print(len(i.main_text_list), len(i.morph_merged))

labnosh.morph_frequency = analyzer.frequency(labnosh.morph_merged)
pprint(labnosh.morph_frequency)

meals.morph_frequency = analyzer.frequency(meals.morph_merged)
pprint(meals.morph_frequency)

morningjuk.morph_frequency = analyzer.frequency(morningjuk.morph_merged)
pprint(morningjuk.morph_frequency)

easy_food.morph_frequency = analyzer.frequency(easy_food.morph_merged)
pprint(easy_food.morph_frequency)

conven_food.morph_frequency = analyzer.frequency(conven_food.morph_merged)
pprint(conven_food.morph_frequency)

### 토픽모델링

intake.LDA = analyzer.SB_LDA()
intake.LDA.make_lda(intake.morph_joined, ntopic=10)

topic0 = intake.LDA.related_doc(intake.main_text_list, 0)

topic1 = intake.LDA.related_doc(intake.main_text_list, 1)

topic2 = intake.LDA.related_doc(intake.main_text_list, 2)

topic3 = intake.LDA.related_doc(intake.main_text_list, 3)

topic7 = intake.LDA.related_doc(intake.main_text_list, 7)

topic9 = intake.LDA.related_doc(intake.main_text_list, 9)

topic3 = intake.LDA.related_doc(intake.main_text_list, 3)



labnosh.LDA = analyzer.SB_LDA()
labnosh.LDA.make_lda(labnosh.morph_joined, ntopic=10)

meals.LDA = analyzer.SB_LDA()
meals.LDA.make_lda(meals.morph_joined, ntopic=10)

morningjuk.LDA = analyzer.SB_LDA()
morningjuk.LDA.make_lda(morningjuk.morph_joined, ntopic=10)

easy_food.LDA = analyzer.SB_LDA()
easy_food.LDA.make_lda(easy_food.morph_joined, ntopic=10)

conven_food.LDA = analyzer.SB_LDA()
conven_food.LDA.make_lda(conven_food.morph_joined, ntopic=10)

### Word2Vec

intake.SB_word2vec = analyzer.SB_Word2Vec(intake.hashtags_appended)

intake.flavor = intake.SB_word2vec.get_sim_sen('맛', intake.main_hash_dic, intake.main_text_list, 4)


intake.diet = intake.SB_word2vec.get_sim_sen('다이어트', intake.main_hash_dic, intake.main_text_list, 4)


intake.health = intake.SB_word2vec.get_sim_sen('건강', intake.main_hash_dic, intake.main_text_list, 4)


intake.exercise = intake.SB_word2vec.get_sim_sen('운동', intake.main_hash_dic, intake.main_text_list, 4)


intake.morningjuk = intake.SB_word2vec.get_sim_sen('모닝죽', intake.main_hash_dic, intake.main_text_list, 4)


intake.meals = intake.SB_word2vec.get_sim_sen('밀스', intake.main_hash_dic, intake.main_text_list, 4)


intake.gonyak = intake.SB_word2vec.get_sim_sen('곤약젤리', intake.main_hash_dic, intake.main_text_list, 4)




### TFIDF

tfidf = analyzer.SB_Tfidf([intake.morph_merged, labnosh.morph_merged, meals.morph_merged, morningjuk.morph_merged, easy_food.morph_merged, conven_food.morph_merged])

tfidf_of_all = tfidf.tfidf_hangul

for i in tfidf_of_all:
    pprint(i[:10])
    print()

meals_juk_SB_Tfidf = analyzer.SB_Tfidf([meals.morph_merged, morningjuk.morph_merged])

tfidf_meals_juk = meals_juk_SB_Tfidf.tfidf_hangul

for i in tfidf_meals_juk:
    pprint(i[:10])
    print()

intake_meals_SB_Tfidf = analyzer.SB_Tfidf([intake.morph_merged, meals.morph_merged])

tfidf_intake_meals = intake_meals_SB_Tfidf.tfidf_hangul

for i in tfidf_intake_meals:
    pprint(i[:10])
    print()

intake_morningjuk_SB_Tfidf = analyzer.SB_Tfidf([intake.morph_merged, morningjuk.morph_merged])

tfidf_intake_morningjuk = intake_morningjuk_SB_Tfidf.tfidf_hangul

for i in tfidf_intake_morningjuk:
    pprint(i[:10])
    print()

meals_conven_food_SB_Tfidf = analyzer.SB_Tfidf([meals.morph_merged, conven_food.morph_merged])

tfidf_meals_conven_food = meals_conven_food_SB_Tfidf.tfidf_hangul

for i in tfidf_meals_conven_food:
    pprint(i[:10])
    print()

morningjuk_conven_food_SB_Tfidf = analyzer.SB_Tfidf([morningjuk.morph_merged, conven_food.morph_merged])

tfidf_morningjuk_conven_food = morningjuk_conven_food_SB_Tfidf.tfidf_hangul

for i in tfidf_meals_conven_food:
    pprint(i[:10])
    print()

