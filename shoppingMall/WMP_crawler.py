from selenium import webdriver
from bs4 import BeautifulSoup
import os
import re
import time
import pandas as pd
from collections import defaultdict
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
driver_path = os.path.join(os.path.join(BASE_DIR,'driver'),'chromedriver.exe')
driver = webdriver.Chrome(driver_path)
# 크롤링할 페이지할 URL 입력
driver.get('http://search.wemakeprice.com/search?search_cate=top&search_keyword=%EB%9E%A9%EB%85%B8%EC%89%AC&_service=5&_type=3')
'http://search.wemakeprice.com/search?search_cate=top&search_keyword=%EB%9E%A9%EB%85%B8%EC%89%AC&_service=5&_type=3'

# 데이터 저장할 Dataframe 생성
df_data = pd.DataFrame(columns = ['mall','corpName','productCode','date','id','productScore','recommScore','main_text'])
#일반 딜 정보 추출
ul = driver.find_element_by_id('search_deal_area')
'''
li_s = spans.find_elements_by_tag_name('li')
#제품이 27개 밖에 없어서 별다른 기능 없이 스크롤 가능
for li in li_s:
    li.click()
    #이렇게 해도 되지만 창을 못 닫는다.
'''

#a tag 클릭(상품 정보)
a_s = ul.find_elements_by_tag_name('a')
cnt_product = 1
#제품이 27개 밖에 없어서 별다른 기능 없이 스크롤 가능.
for a in a_s:
    driver2 = webdriver.Chrome(driver_path)
    driver2.get(str(a.get_attribute('href')))
    time.sleep(2)
    #쇼핑몰,productCode,date,id,productScore,배송별점,추천, main_text 수집
    try:
        driver2.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver2.find_element_by_class_name('tab_ps').click()
    except:
        driver2.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        driver2.find_element_by_class_name('tab_ps').click()

    product_source = driver2.page_source
    soup = BeautifulSoup(product_source,'html.parser')
    regex_between_tab = re.compile('\s.+\s{1}')
    title_with_space = regex_between_tab.findall(soup.find('h4','deal_tit').text)[0]
    title = re.sub('\s','',title_with_space)
    print("TITLE: {0}-------------".format(title))
    #구매main_text 추출
    #리뷰 한페이지 이상 시 버튼 클릭
    reviews_per_product = defaultdict(list)
    while 1:
        #리뷰별 정보 추출
        review_page = driver2.find_element_by_class_name('buy-review-area')
        print("REVIEW_PAGE: {0}------".format(review_page))
        time.sleep(5)
        #가끔 review_list가(reviewpage는들어옴) 제대로 안들어온다. 랜덤한걸로 봐선 시간 문제인듯한데 아니면 구매main_text 버튼 말고 다른걸 클릭한걸수도
        review_list = review_page.find_elements_by_tag_name('li')
        print("REVIEW_LIST: {0}-------------".format(review_list))
        for person_review in review_list:
            r = person_review.text.split('\n')
            print(r)
            if len(r) > 8:
                cnt = len(r) - 8
                reviews_per_product['mall'].append('위메프')
                reviews_per_product['corpName'].append('labnosh')
                reviews_per_product['productCode'].append(200)
                reviews_per_product['date'].append(r[3+cnt+1][:-2])
                reviews_per_product['id'].append(r[1])
                reviews_per_product['productScore'].append(r[0][2:])
                reviews_per_product['recommScore'].append(r[-1])
                reviews_per_product['main_text'].append(''.join(r[3:3+cnt]))

            elif len(r) < 8:
                reviews_per_product['mall'].append('위메프')
                reviews_per_product['corpName'].append('labnosh')
                reviews_per_product['productCode'].append(200)
                reviews_per_product['date'].append(r[3][:-2])
                reviews_per_product['id'].append(r[1])
                reviews_per_product['productScore'].append(r[0][2:])
                reviews_per_product['recommScore'].append(r[-1])
                reviews_per_product['main_text'].append(' ')
            else:
                reviews_per_product['mall'].append('위메프')
                reviews_per_product['corpName'].append('labnosh')
                reviews_per_product['productCode'].append(200)
                reviews_per_product['date'].append(r[3+1][:-2])
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
    df_data = pd.concat([df_data,reviews_pd],ignore_index=True)
    driver2.close()

print(df_data)
with open("wmp_labnosh.pickle","wb") as f:
    pickle.dump(df_data,f,pickle.HIGHEST_PROTOCOL)


driver.close()
# 다 실행하고 난 뒤 키워드에 안맞는 상품의 상품평 삭제 + product code 입력 해줘야 함

"""
# 나중에 데이터베이스에 넣을 때 수정해서 실행해줘야 함

# 데이터 칼럼 지정
df_data = df_data[['mall', 'corpName', 'productCode', 'date', 'id', 'productScore',
                   'recommScore', 'main_text']]

# 데이터베이스 형식에 맞게 수정
df_data['date'] = df_data['date'].apply(lambda x: x[:-3])
df_data['productScore'] = df_data['productScore'].apply(lambda x: x[:-1])

# executemany를 사용하기 위해 각 row를 튜플로 변경해서 data라는 리스트에 할당
data = df_data.values.tolist()
data = [tuple(lst) for lst in data]

# 데이터베이스에 연결
conn = pymssql.connect("intakedb.c63elkxbiwfc.us-east-2.rds.amazonaws.com:1433", "gh", "ghintake", "intake")
cursor = conn.cursor()

# 데이터베이스에 insert
cursor.executemany("insert into productReview values(%s, %s, %d, %s, %s, %d, %d, %s)", data)

# 최종 commit
conn.commit()
conn.close()
"""
