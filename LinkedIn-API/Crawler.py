from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
import gender_guesser.detector as gender
import time
import re
from datetime import datetime
import dotenv
import os

dotenv.load_dotenv('.env', override=True)

class LinkedIn_Crawler:
    def __init__(self, driver=None):
        self.username = os.environ.get('LINKEDIN_USERNAME')
        self.password = os.environ.get('LINKEDIN_PASSWORD')
        self.driver = driver
 
    def start_driver(self, headless=True):
        chrome_options = ChromeOptions()
        chromedriver_autoinstaller.install()
        if headless:
            chrome_options.add_argument("--headless")
        self.driver = Chrome(options=chrome_options)

    def login(self):
        self.driver.get("https://linkedin.com/uas/login")
        email_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        password_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        submit_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
        email_field.send_keys(self.username)
        password_field.send_keys(self.password)
        submit_button.click()
        self.handle_security_verification()

    def handle_security_verification(self):
        title = self.driver.find_element(by=By.TAG_NAME, value='title').get_attribute('innerHTML')
        if 'Security Verification' in title:
            print("Verification Required")
            print("Check Email For Verification Code")
            securityCode = input("Enter Security Code: ")
            print(securityCode)
            security_code_field = self.driver.find_element(by=By.ID,value='input__email_verification_pin').send_keys(securityCode)
            submit_button = self.driver.find_element(by=By.ID,value='email-pin-submit-button').click()

    def get_soup(self):
        return BeautifulSoup(self.driver.page_source, from_encoding="utf-8", features="lxml")

    def is_company(self, input_link):
        return 'company' in input_link

    def create_link(self, input):
        input_link = f'https://www.linkedin.com/company/{input}' if 'linkedin' not in input else input
        print(input_link)
        return input_link
    
    def date_utc(self):
        today_format = str(datetime.utcnow())
        return today_format
    
    def load_posts_count(self, load=10):
        CSS_SELECT = ('button.artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--full.artdeco-button--secondary.ember-view.scaffold-finite-scroll__load-button')
        for _ in range(load):
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, CSS_SELECT)))
                self.driver.find_element(by=By.CSS_SELECTOR, value=CSS_SELECT).click()
            except TimeoutException:
                break

    def set_posts_filter(self):
        DROPDOWN_TRIGGER = 'artdeco-dropdown__trigger.artdeco-dropdown__trigger--placement-bottom.ember-view.display-flex.t-normal.t-12.t-black--light'
        FILTER_BUTTON = 'artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--full.artdeco-button--tertiary.ember-view.justify-flex-start.ph4'

        time.sleep(1)
        check_sortby = self.driver.find_element(by=By.CLASS_NAME, value=DROPDOWN_TRIGGER.replace(' ', '.')).text
        while 'Recent' not in check_sortby:
            self.driver.find_element(by=By.CLASS_NAME, value=DROPDOWN_TRIGGER.replace(' ', '.')).click()
            time.sleep(1)
            try:
                self.driver.find_element(by=By.CLASS_NAME, value=FILTER_BUTTON.replace(' ', '.')).click()
            except:
                pass
            check_sortby = self.driver.find_element(by=By.CLASS_NAME, value=DROPDOWN_TRIGGER.replace(' ', '.')).text

    def crawl_posts(self):
        SCROLL_LOAD_BUTTON = 'button.artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--full.artdeco-button--secondary.ember-view.scaffold-finite-scroll__load-button'
        POST_SELECTOR = 'div.ember-view.occludable-update'

        count = 1
        data_posts = {}
        self.select_posts()
        self.load_posts()
        
        soup = self.get_soup()
        containers = soup.findAll("div", {'class': 'ember-view occludable-update'})

        for container in containers:
            data_dict = self.extract_data(container)
            if data_dict:
                data_posts[count] = data_dict
                count += 1
            if count == 100:
                break

        return data_posts

    def select_posts(self):
        try:
            potent = self.driver.find_element(by=By.CSS_SELECTOR, value='button.artdeco-pill.artdeco-pill--slate.artdeco-pill--3.artdeco-pill--choice.ember-view.mr1.mb2')
            for i in potent:
                if i.text == 'Posts':
                    i.click()
        except:
            pass
    def load_posts(self):
        SCROLL_LOAD_BUTTON = 'button.artdeco-button.artdeco-button--muted.artdeco-button--1.artdeco-button--full.artdeco-button--secondary.ember-view.scaffold-finite-scroll__load-button'
        for _ in range(12):
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, SCROLL_LOAD_BUTTON)))
                self.driver.find_element(by=By.CSS_SELECTOR, value=SCROLL_LOAD_BUTTON).click()
            except TimeoutException:
                break

    def extract_data(self, container):
        data_dict = {}
        try:
            posted_date = container.find("span", {"class": "update-components-actor__sub-description t-black--light t-12 t-normal"}).find("span", {"class": "visually-hidden"})
            text_box = container.find("span", {"class": "break-words"})
            text = text_box.find((text_box.find("span", {"dir": "ltr"})))
            new_likes = container.find("span", {"class": "social-details-social-counts__reactions-count"})
            new_comments = container.find("li", {"class": "social-details-social-counts__item social-details-social-counts__comments social-details-social-counts__item--with-social-proof"})
            
            data_dict = {
                'post_dates': posted_date.text.strip(),
                'post_texts': text_box.text.strip(),
                'post_likes': new_likes.text.strip(']') if new_likes else 0,
                'post_comments': new_comments.text.strip() if new_comments else 0
            }
        except:
            pass
        return data_dict

    def posts_crawler_process(self, posts_link):
        self.driver.get(posts_link)
        try: self.set_posts_filter()
        except: pass
        time.sleep(2)
        self.load_posts_count()
        return self.crawl_posts()
