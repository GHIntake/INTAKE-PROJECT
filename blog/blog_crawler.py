
# coding: utf-8

# In[1]:


from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
import pandas as pd

driver = webdriver.Chrome('/Users/renz/Downloads/chromedriver_win32/chromedriver.exe')
driver.set_window_size(1800, 1000)
driver.maximize_window()
driver.get('https://search.naver.com/search.naver?sm=tab_hty.top&where=post&query=%EC%9D%B8%ED%85%8C%EC%9D%B4%ED%81%AC+-%EC%97%94%EC%A7%84+-%EC%9E%A5%EC%B0%A9+-%ED%81%AC%EB%A6%AC%EB%8B%9D+-%ED%81%B4%EB%A6%AC%EB%8B%9D+-%ED%9D%A1%EA%B8%B0+-RTA&oquery=%EC%9D%B8%ED%85%8C%EC%9D%B4%ED%81%AC+-%EC%97%94%EC%A7%84+-%EC%83%B5%EC%9D%B8%ED%85%8C%EC%9D%B4%ED%81%AC+-%EC%9E%A5%EC%B0%A9+-%ED%81%AC%EB%A6%AC%EB%8B%9D+-%ED%81%B4%EB%A6%AC%EB%8B%9D+-%ED%9D%A1%EA%B8%B0+-RTA&tqi=T0N22lpySDossv%2BgWqRssssstid-426222')

total_blog = pd.DataFrame()

for i in range(2):
    
    post_links = driver.find_elements_by_css_selector('#elThumbnailResultArea > li > dl > dt > a')

    for i in post_links:
        try:
            temp_row = {'keyword':'intake', 'created_at': None, 'post_name': None, 'main_text':None, 'current_url':None}
            i.click()
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)
            driver.switch_to.frame(driver.find_element_by_css_selector('#mainFrame'))
            maintext = driver.find_element_by_css_selector('div.se_doc_viewer > div.se_component_wrap.sect_dsc.__se_component_area')
            sentences = maintext.text.strip()
            print(sentences)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            temp_row['created_at'] = '2018-01-01'
            temp_row['post_name'] = 'postname'
            temp_row['main_text'] = sentences
            temp_row['current_url'] = 'this is current url'

            total_blog = total_blog.append(temp_row, ignore_index=True)

        except NoSuchElementException:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            pass

        if i ==4:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")


    nextbutton = driver.find_element_by_css_selector('#main_pack > div.paging > a.next')
    nextbutton.click()

total_blog = total_blog[['keyword', 'created_at', 'post_name', 'main_text', 'current_url']]

print(total_blog)