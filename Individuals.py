
import gender_guesser.detector as gender
import time
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Crawler import LinkedIn_Crawler


class UserCrawler(LinkedIn_Crawler):

    def user_basic_info(self):
        d = gender.Detector() 
        user_profile = self.get_soup()
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
        user_gender = (d.get_gender(split_name[0])+"^ ")
        try:
            location = self.driver.find_element(by=By.CLASS_NAME, value='text-body-small inline t-black--light break-words'.replace(' ', '.')).text
            headline = user_profile.find('div',{"class":"text-body-medium break-words"}).text.strip()
            bio = self.driver.find_element(by=By.CLASS_NAME,
                    value="pv-shared-text-with-see-more full-width t-14 t-normal t-black display-flex align-items-center".replace(' ','.')).find_element(
                    by=By.CLASS_NAME, value="visually-hidden").text
            followersContainer = self.driver.find_element(by=By.CLASS_NAME, value= 'pvs-header__subtitle.pvs-header__optional-link.text-body-small')
            followers = followersContainer.find_element(by=By.CLASS_NAME, value= 'visually-hidden').text
            liker_locations = location.strip() 
            liker_headlines = (headline.strip())
        except:
            
            liker_locations = ("No Location")
            liker_headlines = ("No Headline")
            bio = ('No Bio')

        basic_info = {'full_name':full_name,'First':first_name,'Last':last_name,'Gender':user_gender[:-2],'Headline':liker_headlines,'Location':liker_locations,'Followers':followers,'Bio':bio}
        return basic_info

    def user_edu_exp(self):
        edu_container = []
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'education')))
        soup = self.get_soup()
        edu_section = soup.find('div', {'id': 'education'}).find_next('div', {'class': 'pvs-list__outer-container'})
        cards = edu_section.find_all('li', {'class': "artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"})
        for i in cards:
            try:
                institution  = (i.find('span',{'class':"mr1 hoverable-link-text t-bold"}).find('span',{'class':"visually-hidden"}).text)
                degree = (i.find('span',{'class':"t-14 t-normal"}).find('span',{'class':"visually-hidden"}).text)
                date = (i.find('span',{'class':"t-14 t-normal t-black--light"}).find('span',{'class':"visually-hidden"}).text)
                education = {'School': institution, 'Degree': degree, 'Date': date}
                edu_container.append(education)
            except: return []
        return edu_container

    def get_user_experiences(self):
        experiences_container = []
        experiences = self.get_soup().find('div', {'id':'experience'}).find_next('ul',{'class':'pvs-list'}).find_all('li',{'class':'artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column'})
        for i in experiences:
            position = i.find('span',{'class':"mr1 t-bold"}).find('span',{'class':"visually-hidden"}).text
            company = i.find('span',{'class':"t-14 t-normal"}).find('span',{'class':"visually-hidden"}).text
            duration = i.find('span',{'class':"t-14 t-normal t-black--light"}).find('span',{'class':"visually-hidden"}).text
            description = i.find('div',{'class':"pvs-list__outer-container"}).find('div',{'class':'pv-shared-text-with-see-more full-width t-14 t-normal t-black display-flex align-items-center'}).find('span',{'class':"visually-hidden"}).text
            experience = {'Position':position,'Company':company,'Duration':duration,'Description':description}    
            experiences_container.append(experience)
        return experiences_container
    

    def get_all_user_data(self, input_link, driver):
        self.driver = driver
        self.driver.get(input_link)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'body')))
        user_info = self.user_basic_info()
        save_name = user_info['First'] + '_' + user_info['Last']
        if save_name is None:
            print('Individual Not Found')
            return None
        else:
            print('Save Name =', save_name)
            user_info.pop('full_name')
            full_name = user_info['First'] + ' ' + user_info['Last']
            user_edu = self.user_edu_exp()
            user_exp = self.get_user_experiences()
            posts_link = input_link + 'recent-activity/shares/'
            posts_payload = self.posts_crawler_process(posts_link)
            current_date = self.date_utc()
            payload = {'Name': full_name, 'Date': current_date, 'Profile': user_info, 'Education': user_edu, 'Experience': user_exp, 'Posts': posts_payload}
            return payload