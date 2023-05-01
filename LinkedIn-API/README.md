# LinkedIn Crawler

LinkedIn Crawler is a Python package that provides an easy way to extract data from LinkedIn profiles and company pages. It uses Selenium WebDriver and BeautifulSoup for web scraping and parsing the HTML content.

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project directory and add your LinkedIn credentials:

```
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

## Usage

### LinkedIn_Crawler

The `LinkedIn_Crawler` class is the base class for crawling LinkedIn profiles and company pages.

```python
from Crawler import LinkedIn_Crawler

crawler = LinkedIn_Crawler()
crawler.start_driver(headless=True)
crawler.login()
```

### Companies

The `Companies` class inherits from `LinkedIn_Crawler` and provides methods for extracting company information.

```python
from Companies import Companies

company_crawler = Companies()
company_data = company_crawler.get_all_data_by_company('https://www.linkedin.com/company/example/')
```

### UserCrawler

The `UserCrawler` class inherits from `LinkedIn_Crawler` and provides methods for extracting user profile information.

```python
from UserCrawler import UserCrawler

user_crawler = UserCrawler()
user_data = user_crawler.get_all_user_data('https://www.linkedin.com/in/example/', crawler.driver)
```

## Classes

### LinkedIn_Crawler

- `__init__(self, driver=None)`: Initializes the LinkedIn_Crawler object.
- `start_driver(self, headless=True)`: Starts the WebDriver with the specified options.
- `login(self)`: Logs in to LinkedIn using the credentials from the `.env` file.
- `handle_security_verification(self)`: Handles security verification if prompted.
- `get_soup(self)`: Returns a BeautifulSoup object of the current page source.
- `is_company(self, input_link)`: Checks if the input link is a company page.
- `create_link(self, input)`: Creates a LinkedIn company page link from the input.
- `date_utc(self)`: Returns the current date in UTC format.
- `load_posts_count(self, load=10)`: Loads the specified number of posts on a company page.
- `set_posts_filter(self)`: Sets the posts filter to "Recent".
- `crawl_posts(self)`: Crawls the posts on a company page.
- `select_posts(self)`: Selects the "Posts" tab on a company page.
- `load_posts(self)`: Loads the posts on a company page.
- `extract_data(self, container)`: Extracts data from a post container.
- `posts_crawler_process(self, posts_link)`: Crawls the posts on a company page using the specified link.

### Companies

- `company_basics(self)`: Extracts basic company information.
- `get_all_data_by_company(self, input_link)`: Extracts all company data using the specified link.

### UserCrawler

- `user_basic_info(self)`: Extracts basic user information.
- `user_edu_exp(self)`: Extracts user education and experience information.
- `get_user_experiences(self)`: Extracts user experiences.
- `get_all_user_data(self, input_link, driver)`: Extracts all user data using the specified link and WebDriver.

## License

This project is licensed under the MIT License.