from selenium import webdriver
from bs4 import BeautifulSoup
import os
import re
import time
import pandas as pd
from collections import defaultdict
import pickle
import pymssql

driver_path = 'chromedriver.exe'
driver = webdriver.Chrome(driver_path)
driver.implicitly_wait(3)
driver.get('http://search.wemakeprice.com/search?search_cate=top&search_keyword=%EC%9D%B8%ED%85%8C%EC%9D%B4%ED%81%AC&_service=5&_type=3')
driver.implicitly_wait(3)

# 데이터 저장할 Dataframe 생성
df_data = pd.DataFrame(columns = ['mall','corpName','productCode','date','id','productScore','recommScore','main_text'])
#일반 딜 정보 추출
ul = driver.find_element_by_id('search_deal_area')

#a tag 클릭(상품 정보)
a_s = ul.find_elements_by_tag_name('a')
cnt_product = 1

for a in a_s:
    driver2 = webdriver.Chrome(driver_path)
    driver2.get(str(a.get_attribute('href')))
    time.sleep(2)
    # 쇼핑몰,productCode,date,id,productScore,배송별점,추천, main_text 수집
    try:
        driver2.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver2.find_element_by_class_name('tab_ps').click()
    except:
        driver2.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver2.find_element_by_class_name('tab_ps').click()

    product_source = driver2.page_source
    soup = BeautifulSoup(product_source, 'html.parser')
    regex_between_tab = re.compile('\s.+\s{1}')
    title_with_space = regex_between_tab.findall(soup.find('h4', 'deal_tit').text)[0]
    title = re.sub('\s', '', title_with_space)
    print("TITLE: {0}-------------".format(title))
    # 구매main_text 추출
    # 리뷰 한페이지 이상 시 버튼 클릭
    reviews_per_product = defaultdict(list)
    while 1:
        # 리뷰별 정보 추출
        review_page = driver2.find_element_by_class_name('buy-review-area')
        # print("REVIEW_PAGE: {0}------".format(review_page))
        time.sleep(5)
        # 가끔 review_list가(reviewpage는들어옴) 제대로 안들어온다. 랜덤한걸로 봐선 시간 문제인듯한데 아니면 구매main_text 버튼 말고 다른걸 클릭한걸수도
        review_list = review_page.find_elements_by_tag_name('li')
        # print("REVIEW_LIST: {0}-------------".format(review_list))
        for person_review in review_list:
            r = person_review.text.split('\n')
            print(r)
            print(len(r))

            if len(r) > 7:
                cnt = len(r) - 7
                reviews_per_product['mall'].append('위메프')
                reviews_per_product['corpName'].append('intake')
                reviews_per_product['productCode'].append(r[2])
                reviews_per_product['date'].append(r[-3][:-2])
                reviews_per_product['id'].append(r[1])
                reviews_per_product['productScore'].append(r[0][2:])
                reviews_per_product['recommScore'].append(r[-1])
                reviews_per_product['main_text'].append(''.join(r[3:3 + cnt]))

            elif len(r) < 7:
                reviews_per_product['mall'].append('위메프')
                reviews_per_product['corpName'].append('intake')
                reviews_per_product['productCode'].append(r[2])
                reviews_per_product['date'].append(r[-3][:-2])
                reviews_per_product['id'].append(r[1])
                reviews_per_product['productScore'].append(r[0][2:])
                reviews_per_product['recommScore'].append(r[-1])
                reviews_per_product['main_text'].append(' ')
            else:
                reviews_per_product['mall'].append('위메프')
                reviews_per_product['corpName'].append('intake')
                reviews_per_product['productCode'].append(r[2])
                reviews_per_product['date'].append(r[-3][:-2])
                reviews_per_product['id'].append(r[1])
                reviews_per_product['productScore'].append(r[0][2:])
                reviews_per_product['recommScore'].append(r[-1])
                reviews_per_product['main_text'].append(r[3])

        try:
            print("---------------TRY NEXT----------------------")
            driver2.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            driver2.find_element_by_class_name('btn_next').click()
        except:
            print("---------------------on except---{0} product".format(cnt_product))
            cnt_product += 1
            break
    reviews_pd = pd.DataFrame.from_dict(reviews_per_product, orient='index').transpose()
    print(reviews_pd)
    df_data = pd.concat([df_data, reviews_pd], ignore_index=True)
    driver2.close()

df_data = df_data[['mall', 'corpName', 'productCode', 'date', 'id', 'productScore',
                   'recommScore', 'main_text']]

df_data['date'] = df_data['date'].str.replace('.','-')
df_data['date'] = df_data['date'][:-6]

# productCode를 품명에서 코드로 바꿔주고 DB에 업데이트
