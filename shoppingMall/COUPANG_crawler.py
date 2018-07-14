import requests
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time

keyword = "랩노쉬"

driver = webdriver.Chrome('/Users/renz/Downloads/chromedriver_win32/chromedriver.exe')
driver.implicitly_wait(3)
driver.get("http://www.coupang.com/")
driver.implicitly_wait(3)

driver.find_element_by_name("q").send_keys(keyword)
driver.find_element_by_xpath('//*[@id="headerSearchBtn"]').click()


page = requests.get(driver.current_url)
soup = BeautifulSoup(page.content, 'html.parser')

product_list_tag = soup.find('ul', id = 'productList', class_ = "search-product-list")

product_ids = [k.strip() for k in str(product_list_tag).split('[')[1].split(']')[0].split(',')]

total_review = []

window_num = 0

for id in product_ids:
    driver.find_element_by_id(id).click()

    window_num += 1
    driver.switch_to.window(driver.window_handles[window_num])  #탭바꾸기
    driver.implicitly_wait(3)

    reviews = []
    present_page = 0
    page_num = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    while True:

        present_page += 1
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')
        review_container = soup2.find("section", class_="js_reviewArticleListContainer")

        scroll_height = 300
        while review_container == None:
            driver.execute_script("window.scrollTo(0, %d)" % (scroll_height))
            driver.implicitly_wait(2)
            soup2 = BeautifulSoup(driver.page_source, 'html.parser')
            review_container = soup2.find("section", class_="js_reviewArticleListContainer")
            scroll_height += 300

        for i in range(1,4):
            driver.execute_script("window.scrollTo(0, %d)" % (scroll_height+50))
            time.sleep(0.1)
            scroll_height += 100





        #상품명
        review_pdname = review_container.find_all('div', class_ = "sdp-review__article__list__info__product-info__name")
        review_pdnames = [n.get_text().strip() for n in review_pdname]

        #작성자이름
        review_id = review_container.find_all('span', class_="sdp-review__article__list__info__user__name js_reviewUserProfileImage")
        review_ids = [n.get_text().strip() for n in review_id]


        #리뷰평
        review_content = review_container.find_all('div', class_ = 'sdp-review__article__list__review__content js_reviewArticleContent')
        review_contents = [c.get_text().strip() for c in review_content]

        #리뷰헤드라인
        review_headline = review_container.find_all('div', class_ = "sdp-review__article__list__headline")
        review_headlines = [h.get_text().strip() for h in review_headline]


        #리뷰 날짜
        review_date = review_container.find_all('div', class_ = 'sdp-review__article__list__info__product-info__reg-date')
        review_dates = [d.get_text().strip() for d in review_date]



        #별점
        review_star = review_container.find_all('div', class_ = "sdp-review__article__list__info__product-info__star-orange js_reviewArticleRatingValue")
        #print(str(review_star[0]).strip().split(" ")[3])
        stars = [int(str(i).strip().split(" ")[3].split('"')[1]) for i in review_star]
        #print(stars)

        #element 개수 맞추기
        review_contents.extend(["No Review" for i in review_dates])
        review_headlines.extend(["No Review Headline" for i in review_dates])




        #supposed to be this long
        #sup_len = soup2.find('div', class_ = "sdp-review__average__total-star__info-count")
            #print(sup_len.get_text())
        #sup_len_ = int(sup_len.get_text())


        #reviews.extend(list(zip(review_pdnames, review_ids, review_contents, review_dates, stars)))

        # reviews 에 추가
        # if len(reviews) < sup_len_:
        #     reviews.extend(list(zip(review_pdnames, review_ids, review_contents, review_dates, stars)))





        try:
            reviews.extend(list(zip(review_pdnames, review_ids, review_headlines, review_contents, review_dates, stars)))
            driver.find_element_by_xpath('//*[@id="btfTab"]/ul[2]/li[2]/div/div[5]/section[4]/div[3]/button[%s]' % (page_num[present_page % 10])).click()
            time.sleep(2)
        except:
           break

    total_review.append(reviews)
    print(reviews)

    driver.switch_to.window(driver.window_handles[0])  #탭바꾸기
    driver.implicitly_wait(3)



print(total_review)


# convert it to a dataframe


a = []
b = []
c = []
d = []
e = []
f = []



for product in total_review:
    a.extend([review[0] for review in product])
    b.extend([review[1] for review in product])
    c.extend([review[2] for review in product])
    d.extend([review[3] for review in product])
    e.extend([review[4] for review in product])
    f.extend([review[5] for review in product])


df = pd.DataFrame({"Product Name" : a, "ID" : b, "Review Headline" : c, "Review Content" : d, "Date" : e, "Ratings" : f})
print(df)

df.to_excel('result1.xlsx', sheet_name= 'sheet1', index = False)