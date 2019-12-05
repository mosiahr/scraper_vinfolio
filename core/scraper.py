import os
import sys
import csv
import time
from random import uniform

from bs4 import BeautifulSoup
from selenium import webdriver
from pyvirtualdisplay import Display

from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from abc import abstractmethod

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils import run_time

BASE_URL = 'https://www.vinfolio.com/shop-wine/allWine?show=100'
FILE = 'out.csv'


class AbstractScraper:
    __url: str = ''
    __driver: webdriver.Firefox

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @abstractmethod
    def start_driver(self, profile) -> None:
        """Starts a new local session of Firefox."""
        ...

    @abstractmethod
    def stop_driver(self) -> None:
        """Stops a own local session of Firefox."""
        ...

    @abstractmethod
    def parsing(self) -> None:
        """Parsing """
        ...

    @abstractmethod
    def save_header(self, path) -> None:
        """Saving headers in file"""
        ...

    @abstractmethod
    def save(self, item, path) -> None:
        """Saving items"""
        ...


class Scraper(AbstractScraper):
    def __init__(self, url: str, display: bool=False, profile: bool=False) -> None:
        self.url = url
        self.display = display
        self.start_driver(profile=profile)

    def start_driver(self, profile: bool) -> None:
        """Starts a new local session of Firefox.
        :return webdriver
        """

        # Start display
        if self.display:
            self.vdisplay = Display(visible=0, size=(1024, 768))
            self.vdisplay.start()

        # Start browser
        ## get the Firefox profile object
        firefoxProfile = None
        if profile:
            firefoxProfile = FirefoxProfile()
            ## Disable CSS
            firefoxProfile.set_preference('permissions.default.stylesheet', 2)
            ## Disable images
            firefoxProfile.set_preference('permissions.default.image', 2)
            ## Disable Flash
            firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
            ## Disable JS
            firefoxProfile.set_preference("javascript.enabled", 'false')

        ## Use the driver
        self.driver = webdriver.Firefox(firefox_profile=firefoxProfile)
        self.driver.maximize_window()
        # self.driver.wait = WebDriverWait(self.driver, 15)

    def stop_driver(self) -> None:
        """Stops a own local session of Firefox.

        :return None
        """
        # Stop browser
        self.driver.quit()

        # Stop display
        if self.display:
            self.vdisplay.stop()

    def click_confirm(self) -> None:
        # Click on the button confirm
        try:
            self.driver.find_element_by_xpath('//*[@id="site-header"]/div[1]/div/div/div/div[3]/button').click()
        except Exception as e:
            print('[No the button confirm]', e)

        # Close the form - "Join us"
        try:
            justuno_form = self.driver.find_element_by_id("justuno_form")
        except:
            justuno_form = None

        if justuno_form:
            self.driver.find_element_by_css_selector('div.design-layer').click()

    def get_driver(self, url, timeout=1, period=1):
        self.driver.get(url)
        if self.driver.execute_script("return document.readyState;") == 'complete':
            self.wait(timeout, period)

    def wait(self, timeout, period):
        try:
            time.sleep(uniform(timeout, timeout + period))
            self.driver.find_element_by_css_selector('#banner-footer')
        # except NoSuchElementException as e:
        except:
            # print(e)
            print('Reload...')
            self.wait(timeout, period + 2)

    def parsing(self) -> None:
        self.save_header(FILE)
        self.get_driver(self.url, 15)
        # self.driver.get(self.url)

        # Click on the button confirm and/or close the form("Join us")
        self.click_confirm()

        # Count the quantity of pages
        try:
            quantity_pages = self.driver.find_element_by_css_selector('p.global-views-pagination-count').text.split('of')[-1]
            quantity_pages = int(quantity_pages.strip())
            print("[Count pages: {}]".format(quantity_pages))
        except Exception as e:
            print(f'{e.__class__.__name__}(Quantity pages): {e}')
            quantity_pages = None

        # Get pages
        if quantity_pages:
            pages = ['{}&page={}'.format(self.url, page) for page in range(1, quantity_pages + 1)]
            print(pages)

            for page in pages:
                self.get_driver(page, 2)

                # Get links items
                links = [a.get_attribute('href') for a in self.driver.find_elements_by_css_selector(
                    '.facets-facet-browse-items a.facets-item-cell-grid-title')]
                print(links, links.__len__())
                for link in links:
                    try:
                        ##### Scraping an item
                        items = ItemScraper(self.driver, link).parsing()
                        self.save(items, FILE)
                    except Exception as e:
                        print(e)
                        items = None
                    # print(items)
        else:
            print('Slow connection. Try to run script again')
        self.stop_driver()

    def save_header(self, path) -> None:
        with open(path, 'w') as csvfile:
            writer = csv.writer(csvfile)
            row_field = (
                'Link', 'Name', 'productname'
            )
            for el in range(1, 8):
                row_field = row_field + (
                    'Price {}'.format(el), 'Count {}'.format(el), 'Label {}'.format(el), 'Message {}'.format(el),
                )
            writer.writerow(row_field)

    def save(self, item, path) -> None:
        with open(path, 'a') as csvfile:
            writer = csv.writer(csvfile)

            row = (
                (item[0]),
                (item[1]),
                (item[2]),
            )

            if item[3]:
                for i in range(0, len(item[3])):
                    for el in item[3][i]:
                        row = row + (el,)

            writer.writerow(row)


class ItemScraper(Scraper):
    def __init__(self, browser: webdriver.Firefox, url: str, display: bool =False, profile: bool =False) -> None:
        self.url = url
        self.driver = browser
        self.display = display
        self.profile = profile

    def parsing(self) -> list:
        '''Scraping a single item. '''
        print('{} Scraping: {}'.format('=' * 5, self.url))

        self.get_driver(self.url, 2)
        # time.sleep(3)

        # Click on the button confirm
        self.click_confirm()

        soup = BeautifulSoup(self.driver.page_source, 'lxml')

        try:
            name = soup.find('h1', class_='product-details-full-content-header-title').text.strip()
        except:
            name = None

        try:
            image_productname = soup.find('div', class_='image-productname').text.strip()
        except:
            image_productname = None

        try:
            container_price = soup.find('div',
                                        class_='custcol_vf_soldby-controls product-views-option-tile-container'
                                               ' product-views-option-tile-container-text')
            prices = container_price.find_all('input', attrs={'name': 'custcol_vf_soldby'})
            price = []
            for p in prices:
                try:
                    _p = p['data-label-price'].lstrip('$').strip()
                except:
                    _p = None

                try:
                    _qty = p['data-label-qty']
                except:
                    _qty = None

                try:
                    _label = p['data-label']
                except:
                    _label = None

                try:
                    _msg = p['data-label-ship-msg']
                except:
                    _msg = None

                price.append((_p, _qty, _label, _msg))

        except:
            price = None
        return [self.url, name, image_productname, price]


@run_time
def main():
    scraper = Scraper(BASE_URL, profile=True)
    scraper.parsing()

if __name__ == '__main__':
    main()