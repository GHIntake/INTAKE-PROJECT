import requests
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time

keyword = "인테이크"    #"랩노쉬"

driver = webdriver.Chrome('/Users/renz/Downloads/chromedriver_win32/chromedriver.exe')
driver.implicitly_wait(3)

blog_url= []

for i in range(67):     #랩노쉬: 78
    driver.get("https://search.daum.net/search?w=blog&m=board&collName=blog_total&q="+keyword+"&spacing=0&DA=PGD&page="+str(i))
    driver.implicitly_wait(3)
    '''
    driver.find_element_by_name("q").send_keys(keyword)
    driver.find_element_by_xpath('//*[@id="daumSearch"]/fieldset/div/div/button[2]').click()
    driver.find_element_by_xpath('//*[@id="blogExtMore"]').click()
    '''
    page = requests.get(driver.current_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    blog_url_list = soup.findAll('a', {'class':"f_link_b"})

    for k in blog_url_list:
        url = str(k).split('="')[2].split('"')[0]

        if 'blog.naver.com' in url:
            url = url.replace('PostView.nhn?blogId=', '')
            url = url.replace('&amp;logNo=', '/')

        blog_url.append(url)

    print(len(blog_url))

naver_blog_url = []
for url in blog_url:
    if 'blog.naver.com' in url:
        naver_blog_url.append(url)

print(naver_blog_url)

for url in blog_url:
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        driver.maximize_window()
    except:
        pass
'''
driver.get("https://blog.naver.com/ynana1/221310303563")
driver.implicitly_wait(10)
driver.maximize_window()

driver.switch_to.frame(driver.find_element_by_name("mainFrame"))
temp = driver.find_element_by_xpath('//*[@id="SEDOC-1530455611747-145288719"]/div[6]/div[1]/div/div/div/div/div/p').text
print(temp)
'''
