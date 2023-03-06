# LinkedIn Data Extractor
This script can extract posts data from a LinkedIn profile page. It uses Python and Selenium with a Chrome driver to log in to a LinkedIn account, crawl through posts on the page, and extract relevant data.

## P.S.
I wrote the scripts in this repo shortly after learning python, so note that the quality of the code is very, very mid

## Usage
Clone the repository:
* git clone https://github.com/username/linkedin-data-extractor.git
* Must add LinkedIn username and password as Enviornment Variables

### Import and initialize API
 ```python
Import LinkedInAPI 
api = linkedInPush.LinkedInAPI(username, password, driver)

```
### Get Company Data
```python
company_link = 'https://www.linkedin.com/company/openai/'
api.main(company_link)
```

### Get Individual Data
```python
individual_link = 'https://www.linkedin.com/in/lexfridman/'
api.main(individual_link)
```

* The script will open a Chrome browser and log in to your LinkedIn account. After that, it will start extracting data from posts on your profile page. The script will output the data to a CSV file named posts_data.csv.

* Limitations
* This script is intended for personal use only.
## Contributors
* This script was written by Darien Nouri. Feel free to contribute to the project by forking the repository and submitting pull requests.
