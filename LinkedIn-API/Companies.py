
import time
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Crawler import LinkedIn_Crawler

class Companies(LinkedIn_Crawler):

    def company_basics(self):
        soup = self.get_soup()
        name = self.find_element_text(soup, 'h1', "ember-view t-24 t-black t-bold full-width", 'null')
        industry = self.find_element_text(soup, 'div', "org-top-card-summary-info-list__info-item", 'null')
        company_website = self.find_element_text(soup, 'a', "link-without-visited-state ember-view", 'null')
        phone_numbers = soup.find_all('span', {'class': "link-without-visited-state"})
        def find_phone(text):
            for i in re.finditer(r"\d{3}[-\.\s]\d{3}[-\.\s]\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]\d{4}|\d{3}[-\.\s]\d{4}", text):
                return i.group(0)
            return ''
        phone_num = ''.join(list(filter(None, [find_phone(i.text) for i in phone_numbers])))
        employee_count = self.find_element_text(soup, 'dd', "t-black--light text-body-small mb1", 'null')
        employees_on = self.find_element_text(soup, 'dd', "t-black--light mb4 text-body-small", 'null')
        employees_on_linkedin = employees_on[:employees_on.index(" on LinkedIn")] if employees_on != 'null' else 'null'
        founded_specialty_raw = soup.find_all('dd', {'class': "mb4 t-black--light text-body-small"})
        founded_on = ''
        for i in founded_specialty_raw:
            year = ''.join(list(filter(str.isdigit, i.text.strip())))
            if year:
                founded_on = year; break

        address = self.find_element_text(soup, 'p', "t-14 t-black--light t-normal break-words", 'none or multiple')
        headquarters = soup.find('dt', text="Headquarters")
        if headquarters:
            try: address = headquarters.find_next_sibling('dd').text.strip()
            except: address = 'null'
        specialties = ''
        for i in soup.find_all('dd', {'class': "mb4 text-body-small t-black--light"}):
            try:
                temp = i.text.strip()
                if ',' in temp and len(temp.split(',')) > 3:
                    specialties = temp
                    break
            except: pass
        params = [name, industry, specialties, founded_on, company_website, phone_num, employee_count, employees_on_linkedin, address]
        params = ['null' if not i else i for i in params]
        return dict(zip(['Company Name', 'Industry', 'Specialties', 'Founded', 'Company Website', 'Phone Number', 'Size', 'Employees On LinkedIn', 'Address'], params))

    def get_all_data_by_company(self, input_link):
        print('Company')
        information = 'Company Profile'
        current_date = self.date_utc()
        about_link = f'{input_link}/about/'
        self.driver.get(about_link)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'content')))
        time.sleep(3)
        company_info = self.company_basics()
        print(company_info)
        save_name = company_info.get('Company Name')
        if save_name is not None:
            posts_link = f'{input_link}/posts/?feedView=all'
            self.driver.get(posts_link)
            self.set_posts_filter()
            posts_payload = self.crawl_posts()
            payload = {
                'Company_Name': company_info['Company Name'],
                'Date': current_date,
                'Profile': company_info,
                'Company_Posts': posts_payload
            }
            return payload
    