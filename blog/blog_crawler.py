
# coding: utf-8

# In[1]:


from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import requests
import pymssql


driver = webdriver.Chrome('/Users/renz/Downloads/chromedriver_win32/chromedriver.exe')
driver.set_window_size(1800, 1000)
driver.maximize_window()
driver.get('https://search.naver.com/search.naver?sm=tab_hty.top&where=post&query=%EC%9D%B8%ED%85%8C%EC%9D%B4%ED%81%AC+-%EC%97%94%EC%A7%84+-%EC%9E%A5%EC%B0%A9+-%ED%81%AC%EB%A6%AC%EB%8B%9D+-%ED%81%B4%EB%A6%AC%EB%8B%9D+-%ED%9D%A1%EA%B8%B0+-RTA&oquery=%EC%9D%B8%ED%85%8C%EC%9D%B4%ED%81%AC+-%EC%97%94%EC%A7%84+-%EC%83%B5%EC%9D%B8%ED%85%8C%EC%9D%B4%ED%81%AC+-%EC%9E%A5%EC%B0%A9+-%ED%81%AC%EB%A6%AC%EB%8B%9D+-%ED%81%B4%EB%A6%AC%EB%8B%9D+-%ED%9D%A1%EA%B8%B0+-RTA&tqi=T0N22lpySDossv%2BgWqRssssstid-426222')



conn = pymssql.connect("intakedb.c63elkxbiwfc.us-east-2.rds.amazonaws.com:1433", "gh", "ghintake", "intake")
cursor = conn.cursor()

def datetime(x):
    y = x.split('. ')
    if len(y[1])==1:
        y[1] = '0'+y[1]
    if len(y[2])==1:
        y[2] = '0'+y[2]
    ysplited = y[3].split(':')
    for i in range(2):
        if len(ysplited[i]) ==1:
            ysplited[i] = '0' + ysplited[i]
    y[3] = ysplited[0] + ":" + ysplited[1]
    z = y[0]+'-'+y[1]+'-'+y[2]+' '+ y[3]
    return z

for j in range(1):
    total_blog = pd.DataFrame()
    post_links = driver.find_elements_by_css_selector('#elThumbnailResultArea > li > dl > dt > a')
    for i in post_links:
        try:
            temp_row = {'keyword':'intake', 'created_at': None, 'post_name': None, 'main_text':None, 'current_url':None}
            i.click()
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)
            driver.switch_to.frame(driver.find_element_by_css_selector('#mainFrame'))
            blog_post_name = driver.find_element_by_css_selector('div:nth-child(3) > div > div > div.pcol1 > div.se_editArea > div > div > div > h3')
            post_name = blog_post_name.text.strip()
            maintext = driver.find_element_by_css_selector('div.se_doc_viewer > div.se_component_wrap.sect_dsc.__se_component_area')
            sentences = maintext.text.strip()
            blog_created_at = driver.find_element_by_css_selector('div:nth-child(3) > div > div > div.se_container > span')
            created_at = blog_created_at.text.strip()
            page = driver.current_url
            blog_current_url = driver.current_url
            #blog_current_url = driver.find_element_by_css_selector('#body > script:nth-child(5)')

#            current_url = blog_current_url.text.strip()

            print(post_name)
            print(sentences)
            print(created_at)
            print(blog_current_url)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            temp_row['post_name'] = post_name
            temp_row['created_at'] = created_at
            temp_row['main_text'] = sentences
            temp_row['current_url'] = blog_current_url

            print(temp_row)

            total_blog = total_blog.append(temp_row, ignore_index=True)

        except NoSuchElementException:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            pass

        if i ==4:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

    if j<99:
        nextbutton = driver.find_element_by_css_selector('#main_pack > div.paging > a.next')
        nextbutton.click()
    else:
        pass

    total_blog['created_at'] = total_blog['created_at'].apply(datetime)
    data = total_blog.values.tolist()
    data = [tuple(lst) for lst in data]
    cursor.executemany("insert into NaverBlogReview (created_at, current_url, keyword, main_text, post_name) values(%s, %s, %s, %s, %s)", data)
    conn.commit()

total_blog = total_blog[['keyword', 'created_at', 'post_name', 'main_text', 'current_url']]
# print(total_blog)


# executemany를 사용하기 위해 각 row를 튜플로 변경해서 data라는 리스트에 할당
# 데이터베이스에 연결
# conn = pymssql.connect("intakedb.c63elkxbiwfc.us-east-2.rds.amazonaws.com:1433", "gh", "ghintake", "intake")
# cursor = conn.cursor()

# 데이터베이스에 insert

# 최종 commit

conn.close()