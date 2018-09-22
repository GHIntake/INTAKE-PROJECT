# INTAKE-PROJECT

Repository for project collaborated with CMR(Convenient Meal Replacement) company 'Intake' with Growth Hackers(SNU business data analysis academic society) members. 

  See more about Growth Hackers: <http://ghmkt.kr/>

## Purpose
The project was conducted in two parts, textming and log data anlysis. 


**1. Textmining**

- Identify consumer awareness of brand Intake
- Analysis the difference between other CMR brand 
- Derive insights that can be useful for product improvement and marketing 


**2. Analysis features by product and behavior pattern in online brand shop** 

- Analysis difference among Intake product and difference among similar product lines with competitor brand using online brand shop review data. 
- Analysis consumer funnel and consumer behavior pattern using online brand shop log data and Google analytics data.
- Derive insights that can be useful for product improvement and marketing 


## Explanation of folder and file inside

**Instagram:** 
   - insta_crawling.ipynb: crawler to collect instagram posting for jupyter notebook 
   - make_mecab_dic.ipynb: New version of social_analysis.ipynb using mecab library for jupyter notebook
   - social_analysis.ipynb: textmining file using konlpy library for jupyter notebook
   - social_analysis.py: textmining file for python idle
   - tutorial_social_analysis.ipynb: tutorial version of social_analysis.ipynb 
   
**blog:** 
   - blog_crawler.py: Naver Blog cralwer
   - blog_crawler.ipynb: Naver Blog cralwer for Jupyter Notebook
   - Blog_analysis.py: Edited version of social_analysis.py for blog analysis

**shoppingMall:**
   - COUPANG_crawler.py: coupang crawler
   - SSG_CMT.csv: SSG review data
   - SSG_CMT_UTF.csv: SSG review data with encoding UTF-8
   - SSG_DATA_PREPROCESS_UPLOAD_DB.ipynb: upload SSG review data after replacing product options with product names
   - SSG_WORD_CSV.csv: product options to be replaced with product names
   - SSG_crawler.ipynb: SSG crawler
   - TMON_crawler.py: TMON crawler
   - WMP_crawler.py: WeMakePrice crawler
   - chromedriver.exe
   - smartstore.py: Naver Smartstore crawler
