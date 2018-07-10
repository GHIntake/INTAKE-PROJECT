from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException, StaleElementReferenceException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
import os
import urllib.request
from collections import Counter
import time
import pickle


class Insta():
    
    user_ids = []
    keyword_dic = {}
    
    def __init__(self, keyword, number, file_name='images', mode='None'):
        self.keyword = keyword
        self.number = number
        self.file_name = file_name
        self.mode = mode

    def chrome_open(self):

        self.options = webdriver.ChromeOptions()
        if self.mode == 'headless':
            self.options.add_argument('headless')
        self.options.add_argument('window-size=1920x1080')
        self.options.add_argument("disable-gpu")
        self.options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        self.options.add_argument("lang=ko_KR") # 한국어!
        self.options.add_argument("disable-infobars")
        self.driver = webdriver.Chrome('chromedriver', chrome_options=self.options)

        self.driver.get('http://google.com')
        self.driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
        self.driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
        self.driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")

        self.driver.implicitly_wait(3)
        
    def insta_keyword(self):
        keyword_t = urllib.parse.urlencode({'': self.keyword})[1:]
        self.driver.get('https://www.instagram.com/explore/tags/{}/?hl=ko'.format(keyword_t))
        #iframe = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'fb_xdm_frame_https')))
        #self.driver.switch_to.frame(iframe1)
        self.total = int(self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/header/div[2]/span/span').text.replace(',', ''))

        
    def crawling(self):
        
        if self.number == 'total':
            number = self.total
        else:
            number = self.number
               
        enter_post = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.eLAPa')))        
        enter_post.click()
        main_text = None
        check_text = True
        checker2 = 0
        for i in range(int(number)):
            if i != 0: check_text = main_text
            start_checker = 0
            same_checker = 0
            #print(start_checker, same_checker, 1)
            #print(start_checker, same_checker, 2)
            while True:       
                try:
                    texts = WebDriverWait(self.driver, 3).until(
                            EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'ul.Xl2Pu > li')))                
                    main_text = texts[0].text
                    comments = [c.text for c in texts[1:]]
                    if check_text == main_text:
                        same_checker += 1
                        if same_checker - start_checker > 200:
                            print(start_checker, same_checker, 3)
                            break
                        continue
                    else: 
                        user_id = WebDriverWait(self.driver, 3).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.e1e1d'))).text
                        break
                except NoSuchElementException as ex:
                    
                    print('completed\n\n', ex)
                except Exception as e:
                    
                    print(i, 'user_id', e)
                    
            if same_checker - start_checker > 200:
                try:
                    next_button = self.driver.find_element_by_css_selector('a.HBoOv.coreSpriteRightPaginationArrow')
                    next_button.click()
                #print(start_checker, same_checker, 4)
                except NoSuchElementException as ex:
                    checker2 += 1
                    print(i, 'user_id', ex)
                    if checker2 > 5:
                        break
                except Exception as e:
                    checker2 += 1
                    print(i, 'user_id', e)
                    if checker2 > 50:
                        break
                continue
            '''        
            if '흡기' in main_text:
                next_button = self.driver.find_element_by_css_selector('a.HBoOv.coreSpriteRightPaginationArrow')
                next_button.click()
                continue
            '''

            if not user_id in self.user_ids:
                self.user_ids.append(user_id)
                self.keyword_dic[user_id] = {'user_index' : i, 'user_id' : user_id, 'main_text' : [], 'hashtags' : [], 'created_at': [],'comments' : [], 'likes' : [], 'current_url' : []}
                while True:
                    try:
                        hashtags = [h.text[1:] for h in self.driver.find_elements_by_css_selector('ul.Xl2Pu>li>span>a')]
                        #print(1)
                        created_at = self.driver.find_element_by_css_selector('time._1o9PC.Nzb55').get_attribute('datetime')
                        #print(2)
                        current_url = self.driver.current_url
                        #print(3)
                        
                        # comments = [c.text for c in texts[1:]]
                        # likes = article.find_element_by_css_selector('span.zV_Nj>span').text

                    except NoSuchElementException as ex:
                        print(i, 1, user_id, ex)
                    except Exception as e:
                        print(i, 1, user_id, e)
                        
                    else:
                        self.keyword_dic[user_id]['main_text'].append(main_text)
                        self.keyword_dic[user_id]['hashtags'].append(hashtags)
                        self.keyword_dic[user_id]['created_at'].append(created_at)
                        self.keyword_dic[user_id]['current_url'].append(current_url)
                        self.keyword_dic[user_id]['comments'].append('. '.join(comments))
                        break
                        # self.keyword_dic[user_id]['comments'].append(comments)
                        # self.keyword_dic[user_id]['likes'].append(likes)
                       
            else:
                while True:
                    try:
                        temp_bool = False
                        for m in self.keyword_dic[user_id]['main_text']:
                            if m != main_text:
                                temp_bool = False
                            else: 
                                temp_bool = True
                                break           
                        if temp_bool == False:
                            #print(1)
                            hashtags = [h.text[1:] for h in self.driver.find_elements_by_css_selector('ul.Xl2Pu>li>span>a')]
                            #print(2)
                            created_at = self.driver.find_element_by_css_selector('time._1o9PC.Nzb55').get_attribute('datetime')
                            #print(3)
                            current_url = self.driver.current_url
                            #print(4)
                            # comments = [c.text for c in texts[1:]]
                            # likes = article.find_element_by_css_selector('span.zV_Nj>span').text
                    
                    except NoSuchElementException as ex:
                        print(i, 2, user_id, ex)
                    except Exception as e:
                        print(i, 2, user_id, e)
                    else:
                        self.keyword_dic[user_id]['main_text'].append(main_text)
                        self.keyword_dic[user_id]['hashtags'].append(hashtags)
                        self.keyword_dic[user_id]['created_at'].append(created_at)
                        self.keyword_dic[user_id]['current_url'].append(current_url)
                        self.keyword_dic[user_id]['comments'].append('. '.join(comments))
                        break
                        # self.keyword_dic[user_id]['comments'].append(comments)
                        # self.keyword_dic[user_id]['likes'].append(likes)
                        
                    
            try:
                next_button = self.driver.find_element_by_css_selector('a.HBoOv.coreSpriteRightPaginationArrow')
                next_button.click()
                print(i, 'finished')
            except NoSuchElementException as ex:
                print('completed\n\n', ex)
            except Exception as e:
                print('completed\n\n', e)
            
                
    def save_with_dic(self):
        with open('{}_dic.txt'.format(self.file_name), 'wb') as f:
            pickle.dump(self.keyword_dic, f)
    '''
    def save_with_list(self):
        with open('{}_list.txt'.format(self.keyword), 'wb') as f:
            dataset = self.keyword.values()
            pickle.dump(datasets)
    '''
    def load_data(self, filename):
        with open(filename, 'rb') as f:
            dataset = pickle.load(f)
        return dataset
    
    def main(self):
        self.chrome_open()
        self.insta_keyword()
        self.crawling()
        self.save_with_dic()
        self.driver.quit()
        
        
if __name__ == '__main__':
    _crawler = Insta(keyword = '랩노쉬', number = '10', file_name = 'labnosh', mode='None')
    _crawler.main()
