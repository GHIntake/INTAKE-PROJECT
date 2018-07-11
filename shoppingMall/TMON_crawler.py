import pandas as pd
import time

import pymssql

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

################################################## 수정할부분
# 크롤링할 상품 페이지 주소 입력
url = "http://www.ticketmonster.co.kr/deal/465447106?keyword=%EC%9D%B8%ED%85%8C%EC%9D%B4%ED%81%AC"

# productCode 입력
productCode = 000
##################################################


driver = webdriver.Chrome("chromedriver.exe")
driver.get(url)
driver.implicitly_wait(10)
driver.maximize_window()

review = driver.find_element_by_xpath('//*[@id="tab-navigation"]/div/ul/li[3]/a')
review.click()

wait = WebDriverWait(driver, 100)

# i: 리뷰 count
# j: 별점 긁어오기 위한 변수
# a: 페이지 count

i = 1
j = 2
a = 1

# 데이터 저장할 Dataframe 생성
df_data = pd.DataFrame()

# 크롤링 할 element가 없을때까지 반복
while(1):
    try:
        # 리뷰별 데이터를 임시로 저장하는 temp_row (최종 데이터의 각 row)
        temp_row = {'mall':'TMON', 'corpName': 'intake', 'productCode':productCode, 'date': None,
                    'id':None, 'productScore':None, 'recommScore':None, 'main_text':None}

        print("i값: {}".format(i))

        date = driver.find_element_by_xpath('//*[@id="_reviewList"]/li[{}]/div[3]/span[2]'.format(i)).text
        temp_row['date'] = date
        print("날짜: {}".format(date))

        # 아이디
        id = driver.find_element_by_xpath('//*[@id="_reviewList"]/li[{}]/div[3]/span[1]/span'.format(i)).text
        temp_row['id'] = id
        print("아이디: {}".format(id))

        # 상품 별점
        temp_productScore = driver.find_elements_by_css_selector('div.score_desc')
        productScore = temp_productScore[j].get_attribute('textContent').strip()
        temp_row['productScore'] = productScore
        print("상품별점: {}".format(productScore))

        # 추천수
        recommScore = driver.find_element_by_xpath('//*[@id="_reviewList"]/li[{}]/div[3]/button[1]/em'.format(i)).text
        temp_row['recommScore'] = recommScore
        print("추천수: {}".format(recommScore))

        # 후기 내용
        main_text = driver.find_element_by_xpath('//*[@id="_reviewList"]/li[{}]/div[2]/p'.format(i)).text
        temp_row['main_text'] = main_text
        print("후기 내용: {}".format(main_text))

        # temp_row(리뷰 하나)를 df_data에 할당
        df_data = df_data.append(temp_row, ignore_index=True)

        print('='*20)

        i = i + 1
        j = j + 2

        # 페이지당 20개의 리뷰가 있으므로 20개 긁으면 넘어감
        if i % 20 == 1:
            next_page = driver.find_element_by_xpath('//*[@id="reviewPaginate"]/div/a[@class="next_page"]').click()
            i = 1
            j = 2
            time.sleep(3)
            print("page num: {}".format(a))
            a += 1

    except:
        print("완료")
        break


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

