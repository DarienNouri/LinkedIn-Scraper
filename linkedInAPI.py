from shutil import ExecError
from sqlite3 import Time
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from googlesearch import search
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import chromedriver_autoinstaller
import gender_guesser.detector as gender
from IPython.display import display
import os 
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime
import re
from datetime import date 
import pytz
import dotenv
import warnings
from os import environ
warnings.filterwarnings("ignore")
dotenv.load_dotenv('.env', override=True)

username = environ.get('LINKEDIN_USERNAME')
password = environ.get('LINKEDIN_PASSWORD')


if username is None:
    raise Exception('Make sure to enter a valid username "LINKEDIN_USERNAME"')
if password is None:
    raise Exception('Make sure to enter a valid password "LINKEDIN_PASSWORD"')


class LinkedInAPI:
    def __init__(self, email, password, driver = None):
        self.email = email
        self.password = password
        self.driver = driver

    def startDriver(self):
        self.driver = webdriver.Chrome()
        
    def login(self, email, password):
        self.driver.get("https://linkedin.com/uas/login")
        email_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        password_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        submit_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        email_field.send_keys(email)
        password_field.send_keys(password) 
        submit_button.click()  
        
    def getSoup(self):
        src = self.driver.page_source
        soup = BeautifulSoup(src, from_encoding = "utf-8",features="lxml")
        soup.prettify()
        return soup
    
    def scroll(self, last = 0):
        finalScroll = last+1000
        start = time.time()
        initialScroll = last
        finalScroll = finalScroll
        while True:
            self.driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
            initialScroll = finalScroll
            finalScroll += 1000
            time.sleep(2)
            end = time.time()
            if round(end - start) > 20:
                break
        return finalScroll
    
    def load_posts_count(self, load= 10):
        for post_num in range(load):
            try:
                myElem = WebDriverWait(self.driver, 1,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'button[class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]')))
                self.driver.find_element(by=By.CSS_SELECTOR,value='button[class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]').click()
            except TimeoutException:
                soup = self.getSoup()
                break

    def crawl_posts(self):
        count = 1
        data_posts = {}
        try:
            potent = self.driver.find_element(by=By.CSS_SELECTOR,value='button[class="artdeco-pill artdeco-pill--slate artdeco-pill--3 artdeco-pill--choice ember-view mr1 mb2"]')
            for i in potent:
                if i.text == 'Posts':
                    i.click()
        except:
            pass
        for post_num in range(12):
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR,'button[class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]')))
                self.driver.find_element(by=By.CSS_SELECTOR,value='button[class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--secondary ember-view scaffold-finite-scroll__load-button"]').click()
            except TimeoutException:
                soup = self.getSoup()
                print('fewer than 100 posts')
                break
        soup = self.getSoup()
        containers = soup.findAll("div", {'class':'ember-view occludable-update'})
        soup = self.getSoup()
        containers = soup.findAll("div", {'class':'ember-view occludable-update'})
        for container in containers:   
            data_dict = {}
            #Try function to make sure its a post and not a promotion
            try:
                posted_date = container.find("span",{"class":"feed-shared-actor__sub-description t-12 t-normal t-black--light"}).find("span",{"class":"visually-hidden"})
                text_box = container.find("span",{"class":"break-words"})
                text = text_box.find((text_box.find("span",{"dir":"ltr"})))
                new_likes = container.find("span", {"class":"social-details-social-counts__reactions-count"})
                new_comments = container.find("li", {"class": "social-details-social-counts__item social-details-social-counts__comments social-details-social-counts__item--with-social-proof"})
                #Appending date and text to lists
                post_dates = (posted_date.text.strip())
                post_texts = (text_box.text.strip())                   
                try:
                    post_likes = (new_likes.text.strip(']'))
                except:
                    post_likes = (0)
                    pass
                try:
                    post_comments = (new_comments.text.strip())                           
                except:                                                           
                    post_comments = (0)
                    pass
                 
            except:
                pass
            
            def ago_do_date(self, ago):
                value, unit = re.search(r'(\d+) (\w+) ago', ago).groups()
                if not unit.endswith('s'):
                    unit += 's'
                delta = relativedelta(**{unit: int(value)})
                return ((datetime.now() - delta).date())
            if count == 100:
                break
            post_dates_current = str(ago_do_date(post_dates))
            data_dict = ({'post_dates':post_dates_current,'post_texts':post_texts,'post_likes':post_likes,'post_comments':post_comments})
            data_posts[count] = data_dict
            count+=1
        return data_posts

    def set_posts_filter(self): ##For scraping company posts
        soup = self.getSoup()
        time.sleep(3)
        first_in = self.driver.find_element(by=By.CSS_SELECTOR,value='li-icon[class="sort-dropdown__icon"]')
        check_sortby = first_in.find_element(by=By.XPATH, value= '..').text
        try:
            while 'Recent' not in check_sortby :
                self.driver.find_element(by=By.CSS_SELECTOR,value='button[class="artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom ember-view display-flex t-normal t-12 t-black--light"]').click()
                time.sleep(4)
                self.driver.find_element(by=By.CSS_SELECTOR,value='button[class="artdeco-button artdeco-button--muted artdeco-button--1 artdeco-button--full artdeco-button--tertiary ember-view justify-flex-start ph4"]').click()
                soup = self.getSoup()
                check_sortby = soup.find("button", {'class':'artdeco-dropdown__trigger artdeco-dropdown__trigger--placement-bottom ember-view display-flex t-normal t-12 t-black--light'}).next_element.next_element.text
        except:
            pass
    def check_if_company_or_individual(self, input_link):
        if 'company' in input_link:
            company = True
        else:
            company = False
        return company
    def create_link(input):
        
        if 'linkedin' not in input:
            input_link = 'https://www.linkedin.com/company/'+ input
        else:
            input_link = input
        print(input_link)
    
            
        return input_link
    def company_basics(self):
        soup = self.getSoup()
        name = soup.find('h1',{'class':"ember-view t-24 t-black t-bold full-width"}).text.strip()
        try:
            industry = soup.find('div',{'class':"org-top-card-summary-info-list__info-item"}).text.strip()
            company_website = soup.find('a',{'class':"link-without-visited-state ember-view"}).text.strip()
        except:
            industry = 'null' 
            company_website = 'null'
        phone_check = soup.find_all('span',{'class':"link-without-visited-state"})
        for i in phone_check:
            phone_num = ''
            try:
                check2 = re.search(r"(\d{3}[-\.\s]\d{3}[-\.\s]\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4})",i.text)
                if check2 is not None:
                    phone_num = (i.text.strip())
            except:
                phone_num = ''
                continue    
        try:
            employee_count = soup.find('dd',{'class':"text-body-small t-black--light mb1"}).text.strip()
        except:
            employee_count = 'null'
        try:
            employees_on =  str(soup.find('dd',{'class':"text-body-small t-black--light mb4"}).text.strip())
            employees_on_linkedin = (employees_on[:employees_on.index(" on LinkedIn")])
        except:
            employees_on = 'null'
            employees_on_linkedin = 'null'

        founded_specialty_raw = soup.find_all('dd',{'class':"mb4 text-body-small t-black--light"})
        founded_on = ''
        try:
            for i in founded_specialty_raw:
                check = re.search(r"[0-9]{4}", i.text.strip())
                if  check is not None:
                    value = (i.text.strip())
                    if value.isnumeric():
                        founded_on = (value)
        except:
            founded_on = 'null'    
        try:
            address = soup.find('p',{'class':"t-14 t-black--light t-normal break-words"}).text.strip()
        except:
            address = 'none or multiple'    
        try:
            founded_specialty_raw = soup.find_all('dt',{'class':"mb1 text-heading-small"})
            for i in founded_specialty_raw:
                if 'Headquarters' in i.text:
                            address = i.next_element.next_element.next_element.text.strip()             
        except:
            address = 'null'
        special_raw = soup.find_all('dd',{'class':"mb4 text-body-small t-black--light"})
        specialties = ''
        for i in special_raw:
            try:
                if ',' in (i.text.strip()) and len(i.text.strip().split(','))>3:
                    specialties = i.text.strip()
                    
                    continue
            except:
                specialties = ''    
        params = [name,industry,specialties,founded_on,company_website,phone_num,employee_count,employees_on_linkedin,address]
        for i in params:
            if i not in locals() or len(i) < 1:
                i = 'null'
        company_info_dict = {'Company Name':name,'Industry':industry,'Speialties':specialties,'Founded':founded_on,'Company Website':company_website,'Phone Number':phone_num,'Size':employee_count,'Employees On LinkedIn':employees_on_linkedin,'Address':address}
        return company_info_dict
    
    def user_basic_info(self):
        d = gender.Detector() 
        soup = self.getSoup()
        user_profile = self.getSoup()
        name = user_profile.find('h1',{'class':"text-heading-xlarge inline t-24 v-align-middle break-words"})
        name = name.text.strip()
        try:
            split_name = name.split(" ", 2)
            first_name = split_name[0]
            last_name = split_name[-1]
            full_name = first_name+'_'+last_name
        except:
            first_name = name
            last_name = 'no last name'
            full_name = name
        #Get Liker Gender
        user_gender = (d.get_gender(split_name[0])+"^ ")
        try:
            #Get Liker Location
            location = self.driver.find_element(by=By.CLASS_NAME, value= 'text-body-small inline t-black--light break-words').text
            liker_locations = (location.text.strip()+"^ ")
        except:
            liker_locations = ("No Location")

        try:
            #Get Liker Headline
            headline = user_profile.find('div',{"class":"text-body-medium break-words"}).text.strip()
            liker_headlines = (headline.strip())
        except:
            liker_headlines = ("No Headline")
        try:
                soup = self.getSoup()
            
                self.driver.find_element(by=By.CLASS_NAME, value= "pv-shared-text-with-see-more.t-14.t-normal.t-black display-flex align-items-center").find_element(by=By.CLASS_NAME, value= "visually-hidden").text          
                time.sleep(1)        
        except:
                bio = ('No Bio')
        try:
            followersContainer = self.driver.find_element(by=By.CLASS_NAME, value= 'pvs-header__subtitle.pvs-header__optional-link.text-body-small')
            followers = followersContainer.find_element(by=By.CLASS_NAME, value= 'visually-hidden').text
        except:
            followers = ('No Follower Count') 
        basic_info = {'full_name':full_name,'First':first_name,'Last':last_name,'Gender':user_gender[:-2],'Headline':liker_headlines,'Location':liker_locations,'Followers':followers,'Bio':bio}
        return(basic_info)
    def user_edu_exp(self):##maybe add link arg
        count_edu = 0
        count_exp = 0
        edu_dict = {}
        exp_dict = {}
        soup = self.getSoup()
        cards = soup.find_all('li',{'class':"artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"})
        
        for i in cards:
            try:
                institution  = (i.find('span',{'class':"mr1 hoverable-link-text t-bold"}).find('span',{'class':"visually-hidden"}).text)
                try:
                    degree = (i.find('span',{'class':"t-14 t-normal"}).find('span',{'class':"visually-hidden"}).text)
                except:
                    degree = ('null')
                
                try:
                    date = (i.find('span',{'class':"t-14 t-normal t-black--light"}).find('span',{'class':"visually-hidden"}).text)
                    if count_edu == 1:
                            date_check = date

                    try:
                        date_regex = re.findall(r"[0-9]{4}", date_check)[-1] 
                    except:
                        pass
                    try:
                        local_date_regex = re.findall('[1-3][0-9]{3}',date)  
                        if int(date_regex) < int(local_date_regex[-1]) +5:     
                            continue  
                    except:
                        pass
                except:
                    date= ('null')
                count_edu+=1
                education = {}
                
                education =  {'School':institution,'Degree':degree,'Date':date}
                edu_dict[count_edu] = education
            except:
                try:
                    expi = (i.find('span',{'class':"t-14 t-normal"}).find('span',{'class':"visually-hidden"}).text)
                    exp_date = (i.find('span',{'class':"t-14 t-normal t-black--light"}).find('span',{'class':"visually-hidden"}).text)
                    expiernece = {}
                    expierence  = {'Expierence':expi,'Date':exp_date}  
                    count_exp+=1        
                    exp_dict[count_exp] = expierence
                except:
                    
                    continue
        education_df = (pd.DataFrame.from_dict(edu_dict))
        expierence_df = (pd.DataFrame.from_dict(exp_dict))
        display(education_df)
        display(expierence_df)
        return [edu_dict,exp_dict]
    
    def get_all_data_by_company(self, input_link):
        print('Company')
        information = 'Company Profile'
        current_date = self.date_utc()
        self.driver.get(input_link+'/about/')
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'main')))
        user_info = self.company_basics()
        print(user_info)
        user_edu = {}
        save_name = user_info.get('Company Name')
        if save_name is None:
            posts_link = input_link + '/posts/?feedView=all'
            self.driver.get(posts_link)
            self.set_posts_filter()
            #linkedin.load_posts_count()
            posts_payload = self.crawl_posts()
            payload = {'Company_Name':company_info['Company Name'],'Date':current_date,'Profile':company_info,'Company_Posts': posts_payload}
        else:
            print('Company Not Found')
            return None
        
        
    def get_all_data_by_individual(self, inputLink):
        self.driver.get(inputLink)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'main')))
        user_info = self.user_basic_info()

        save_name = user_info['First']+'_'+user_info['Last']
        if save_name is None:
            print('Individual Not Found')
            return None
        else:
            print('Save Name =',save_name)
            user_info.pop('full_name')
            full_name = user_info['First'] + ' ' + user_info['Last']
            user_edu = self.user_edu_exp()
            posts_link = inputLink + 'recent-activity/shares/'
            self.driver.get(posts_link)
            #linkedin.load_posts_count()
            posts_payload = self.crawl_posts()
            company = 'User Profile'
            current_date = self.date_utc()
            payload = {'Name':full_name,'Date':current_date,'Profile':user_info,'Education':user_edu[0],'Expierence':user_edu[1],'User Posts': posts_payload}
            return payload
    
    def date_utc(self):
        today = date.today()
        today_format = str(datetime.utcnow())
        return today_format
    
    def main(self, input):
        print(self.date_utc())
        self.startDriver()
        self.login(self.email, self.password)
        input_link = self.create_link(input)
        print(input_link)
        company = self.check_if_company_or_individual(input_link)
        
        if company == True:
                payload = self.get_all_data_by_company(input_link)
                save_name = payload['Company_Name']
                print(f'Save Name company = {save_name}')   
        else:
            print('Individual')
            time.sleep(2)
            payload = self.get_all_data_by_individual(input_link)
        if payload:
            with open(save_name+'.json', 'w') as fp:
                json.dump(payload, fp,  indent=4)
            print('Done')
            self.driver.close()
            return payload
        else:
            pass
