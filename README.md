# scraper_vinfolio
Web Scraper that use Selenium Webdriver
<br/><br/>

### Clone the repository 
git clone https://github.com/mosiahr/scraper_vinfolio.git <br>
cd scraper_vinfolio
<br/><br/>

### Create virtual environment and activate it
virtualenv -p python3 venv <br>
source venv/bin/activate <br>
pip install -r requirements.txt
<br/><br/>

### Run
python core/scraper
<br/><br/>

### Task 1. Find all Items
Use:
```
@run_time
def main():
    scraper = Scraper(BASE_URL, profile=True)
    scraper.parsing()
```

### Task 2. Find Items Without Pictures
Use class ScraperWithoutImg:
```
@run_time
def main():
    scraper = ScraperWithoutImg(BASE_URL)
    scraper.parsing()
```
<br/>

### Other
To disable the loading of CSS, images, Flash, WZ, set the class Scraper attribute profile=True <br>
Disable everything but leave javascript enabled use js_enabled: profile=True, js_enabled=True



