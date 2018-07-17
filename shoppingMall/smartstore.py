from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import requests
import pymssql

conn = pymssql.connect("intakedb.c63elkxbiwfc.us-east-2.rds.amazonaws.com:1433", "gh", "ghintake", "intake")
cursor = conn.cursor()

productreview = pd.DataFrame()


driver = webdriver.Chrome('/Users/naljeong/chromedriver/chromedriver')
driver.get('https://smartstore.naver.com/intakdefoods')
categories = driver.find_elements_by_css_selector('#nav > div.layout_inner.is_folded._category_and_menu_area > div > ul.lnb._main_category._category_list > li > a')

# 상품군 6개에 대해 하나씩
for i in range(6):
    category = categories[i]
    category.click()
    if (i == 0) or (i == 3) or (i == 5):
        init_products = driver.find_elements_by_css_selector('#content > div > form > div.module_list_product_default.extend_five.extend_thumbnail_square > ul > li > a.area_overview')
    elif (i == 1) or (i == 2) or (i ==4):
        init_products = driver.find_elements_by_css_selector('#content > div > form > div.module_list_product_default.extend_four.extend_thumbnail_tall > ul > li > a.area_overview')

    # 상품 하나씩
    for j in range(len(init_products)):
        if j == 0:
            product = init_products[0]
        else:
            product = products[j]
        product.click()
        reviewbutton = driver.find_element_by_css_selector('#wrap > div > div.prd_detail_common > div:nth-child(4) > div > div > ul > li:nth-child(2) > a')
        reviewbutton.click()
        time.sleep(1)

        #프리미엄 구매평
        # premiumno = driver.find_element_by_css_selector('#purchase_review_list_premium > form > div.header_review > strong')
        # premiumnotext = premiumno.text.strip()
        # prenoint = int(premiumnotext[9:-1])
        # premreviewprem_pages = prenoint // 10

        prem_decade = 1
        prem_page = 1

        x = 1
        while x:
            try:
                prem_reviews = driver.find_elements_by_css_selector('#purchase_review_list_premium > div.detail_list_review.extend_premium._list_area > ul > li')
                if len(prem_reviews) == 0:
                    break
                else:
                    for prem_review in prem_reviews:
                        temp_row = {'mall':'NaverSmartStore', 'corpName': 'intake', 'productCode': None, 'date': None, 'id': None, 'productScore': None, 'recommScore':-1, 'main_text':None}

                        raw_date = prem_review.find_element_by_css_selector('div.info_review_text > div.area_info > span:nth-child(2)')
                        date_text = raw_date.text.strip()
                        date = date_text.replace('.','-')
                        temp_row['date'] = date

                        raw_id = prem_review.find_element_by_css_selector('div.info_review_text > div.area_info > span.text_info.author')
                        id_text = raw_id.text.strip()
                        id = id_text[4:]
                        temp_row['id'] = id

                        raw_prodscore = prem_review.find_element_by_css_selector('div.row > div.col_label > span')
                        prodscore_text = raw_prodscore.text.strip()
                        if prodscore_text == '적극추천':
                            productScore = 5
                        if prodscore_text == '추천':
                            productScore = 4
                        if prodscore_text == '보통':
                            productScore = 3
                        if prodscore_text =='추천안함':
                            productScore =1
                        temp_row['productScore'] = productScore

                        raw_title = prem_review.find_element_by_css_selector('div.row > div.col_content > div.inner_content > div.review_comment > div.header_review_comment')
                        title_text = raw_title.text.strip()
                        raw_bmaintext = prem_review.find_element_by_css_selector('div.row > div.col_content > div.inner_content > div.review_comment > p')
                        bmaintext_text = raw_bmaintext.text.strip()
                        maintext = title_text + '\n' + bmaintext_text
                        temp_row['main_text'] = maintext

                        raw_productcode = driver.find_element_by_css_selector('#wrap > div > div.prd_detail_basic > div.info > form > fieldset > div._copyable > dl > dt > strong')
                        productcode_text = raw_productcode.text.strip()
                        temp_row['productCode'] = productcode_text

                        productreview = productreview.append(temp_row, ignore_index=True)
                        print(temp_row)

                        if prem_review == prem_reviews[-1]:
                            prem_pages = driver.find_elements_by_css_selector('#purchase_review_list_premium > div.module_pagination > a')
                            if prem_decade == 1:
                                if prem_page <= 9:
                                    print(str(prem_decade-1)+str(prem_page))
                                    if prem_pages[prem_page-1] == prem_pages[-1]:
                                        x=0
                                    else:
                                        next_prem_page = prem_pages[prem_page]
                                        next_prem_page.click()
                                        time.sleep(2)
                                        prem_page += 1
                                else:
                                    print(str(prem_decade-1)+str(prem_page))
                                    next_prem_decade = prem_pages[10]
                                    next_prem_decade.click()
                                    time.sleep(2)
                                    prem_decade += 1
                                    prem_page = 1
                            else:
                                if prem_page <= 9:
                                    print(str(prem_decade-1)+str(prem_page))
                                    if prem_pages[prem_page] == prem_pages[-1]:
                                        x=0
                                    else:
                                        next_prem_page = prem_pages[prem_page+1]
                                        next_prem_page.click()
                                        time.sleep(2)
                                        prem_page += 1
                                else:
                                    print(str(prem_decade-1)+str(prem_page))
                                    next_prem_decade = prem_pages[11]
                                    next_prem_decade.click()
                                    time.sleep(2)
                                    prem_decade += 1
                                    prem_page = 1

            except NoSuchElementException:
                break

        gen_decade = 1
        gen_page = 1

        y = 1
        while y:
            try:
                gen_reviews = driver.find_elements_by_css_selector('#purchase_review_list_general > div.detail_list_review._list_area > ul > li')
                if len(gen_reviews) == 0:
                    break
                else:
                    for gen_review in gen_reviews:
                        temp_row = {'mall':'NaverSmartStore', 'corpName': 'intake', 'productCode': None, 'date': None, 'id': None, 'productScore': None, 'recommScore':-1, 'main_text':None}

                        raw_date = gen_review.find_element_by_css_selector('div.row > div.col_content > div.inner_content > div.review_comment > div.area_info > span:nth-child(2)')
                        date_text = raw_date.text.strip()
                        date = date_text.replace('.','-')
                        temp_row['date'] = date

                        raw_id = gen_review.find_element_by_css_selector('div.row > div.col_content > div.inner_content > div.review_comment > div.area_info > span:nth-child(1)')
                        id_text = raw_id.text.strip()
                        id = id_text[4:]
                        temp_row['id'] = id

                        raw_prodscore = gen_review.find_element_by_css_selector('div.row > div.col_label > span')
                        prodscore_text = raw_prodscore.text.strip()
                        if prodscore_text == '만족':
                            productScore = 5
                        if prodscore_text == '보통':
                            productScore = 3
                        if prodscore_text =='불만':
                            productScore =1
                        temp_row['productScore'] = productScore

                        raw_main = gen_review.find_element_by_css_selector('div.row > div.col_content > div.inner_content > div.review_comment > div.header_review_comment')
                        main_text = raw_main.text.strip()
                        temp_row['main_text'] = main_text

                        raw_productcode = driver.find_element_by_css_selector('#wrap > div > div.prd_detail_basic > div.info > form > fieldset > div._copyable > dl > dt > strong')
                        productcode_text = raw_productcode.text.strip()
                        temp_row['productCode'] = productcode_text

                        productreview = productreview.append(temp_row, ignore_index=True)
                        print(temp_row)

                        if gen_review == gen_reviews[-1]:
                            gen_pages = driver.find_elements_by_css_selector('#purchase_review_list_general > div.module_pagination._purchase_review_list_general_page_area.page-loaded > a')
                            if gen_decade == 1:
                                if gen_page <= 9:
                                    if gen_pages[gen_page-1] == gen_pages[-1]:
                                        y=0
                                    else:
                                        next_gen_page = gen_pages[gen_page]
                                        next_gen_page.click()
                                        time.sleep(2)
                                        gen_page +=1
                                else:
                                    next_gen_decade = gen_pages[10]
                                    next_gen_decade.click()
                                    time.sleep(2)
                                    gen_decade += 1
                                    gen_page = 1
                            else:
                                if gen_page <= 9:
                                    if gen_pages[gen_page] == gen_pages[-1]:
                                        y=0
                                    else:
                                        next_gen_page = gen_pages[gen_page+1]
                                        next_gen_page.click()
                                        time.sleep(2)
                                        gen_page += 1
                                else:
                                    next_gen_decade = gen_pages[11]
                                    next_gen_decade.click()
                                    time.sleep(2)
                                    gen_decade +=1
                                    gen_page =1

            except NoSuchElementException:
                break

        driver.back()
        driver.back()
        time.sleep(2)

        if (i == 0) or (i == 3) or (i == 5):
            products = driver.find_elements_by_css_selector('#content > div > form > div.module_list_product_default.extend_five.extend_thumbnail_square > ul > li > a.area_overview')
        elif (i == 1) or (i == 2) or (i ==4):
            products = driver.find_elements_by_css_selector('#content > div > form > div.module_list_product_default.extend_four.extend_thumbnail_tall > ul > li > a.area_overview')

    categories = driver.find_elements_by_css_selector('#nav > div.layout_inner.is_folded._category_and_menu_area > div > ul.lnb._main_category._category_list > li > a')

productreview = productreview[['mall', 'corpName', 'productCode', 'date', 'id', 'productScore',
                   'recommScore', 'main_text']]
prodlist = productreview['productCode']
prodset = set(prodlist)
# proddict={}
# for prodname in prodset:
#     proddict[prodname] = str(input("Input product code of {0}: ".format(prodname)))
proddict={'13가지 수퍼푸드로 만든 인테이크 수퍼바 10개 세트 (에너지바/슈퍼푸드/수퍼푸드/칼로리바/다이어트바/곡물바)': 14202,
 '13가지 슈퍼푸드로 만든 인테이크 슈퍼바 20개 세트 (에너지바/수퍼바/수퍼푸드/칼로리바/다이어트바/곡물바)': 14202,
 '5가지 견과류로 만든 인테이크 홀넛츠바 20개입 세트 (에너지바/견과바/견과류바/칼로리바/다이어트바)': 14204,
 '[SET] 세상모든 향신료 18종 선물세트': 13303,
 '[인테이크] 모닝죽 단호박/단팥/고구마/귀리 28팩 (식사대용/아침식사/건강식/고구마죽/아침죽)': 12103,
 '[인테이크]간편한 아침 모닝죽 7팩(선택: 단호박/단팥/고구마/귀리/검은콩) (식사대용/아침식사/건강식/고구마죽/아침죽)': 12100,
 '[인테이크]닥터넛츠 오리지널뉴 30개입 (프리미엄견과/하루견과/견과류/피스타치오/아몬드/캐슈넛/피칸/호두)': 14102,
 '[인테이크]닥터넛츠 프리미엄 골드 30개입(프리미엄견과/아몬드/캐슈넛/헤이즐넛/마카다미아/브라질넛/피칸)': 14101,
 '★진짜 귀리99.8%함유★ 모닝 귀리(50g)X6개': 12400,
 '닥터넛츠 2종 견과 선물세트': 14101,
 '더욱 간편해진! 모닝 그래놀라(30g) 7개입 / 125kcal': 12302,
 '모닝수프 감자(30gx7개입)': 12202,
 '모닝수프 스타터 키트(감자2개+양송이2개+채소2개)': 12200,
 '모닝수프 양송이(30gx7개입)': 12201,
 '모닝수프 채소(30gx7개입)': 12203,
 '밀스 라이트 로얄밀크티 1주일패키지(45gx7개)': 11304,
 '밀스 라이트 말차라떼 1주일패키지(50gx7개)': 11301,
 '밀스 라이트 벨벳카카오 1주일패키지(52gx7개)': 11302,
 '밀스 라이트 스윗그레인 1주일패키지(48gx7개)': 11303,
 '밀스 라이트 카페라떼 1주일패키지(50gx7개)': 11300,
 '밀스3.1 그레인 보틀형 1주일패키지(98gx7개)': 11201,
 '밀스3.1 소이 보틀형 1주일패키지(98gx7개)': 11210,
 '밀스3.1 코코넛 보틀형 1주일패키지(98gx7개)': 11202,
 '에센셜 향신료 6종 세트': 13300,
 '에센셜 허브 6종 세트': 13300,
 '인테이크 밀스 전용 쉐이커': 11209,
 '인테이크 홀넛츠바 1Box(10팩x38g)': 14204,
 '칼로리컷 츄어블 딸기맛(2,000mgx42정)': 16301,
 '한끼 149kcal 곤약 백미밥(125g) 10개': 13202,
 '한끼 149kcal 곤약 현미밥(125g) 10개': 13203,
 '한끼 버터치킨 커리(120g) 10개 / 185kcal': 13102,
 '한끼 스파이시 비프 커리(120g) 10개 / 135kcal': 13103}

productreview['productCode'] = productreview['productCode'].apply(lambda x: proddict[x])

data = productreview.values.tolist()
data = [tuple(lst) for lst in data]
cursor.executemany("insert into productReview values(%s, %s, %d, %s, %s, %d, %d, %s)", data)
conn.commit()
conn.close()
