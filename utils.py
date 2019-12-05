import time
import datetime
from random import uniform, choice

import requests
from bs4 import BeautifulSoup

URL_TEST = 'http://sitespy.ru/my-ip'
PROXY = '159.65.229.150:8080'

useragent = \
        {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; chromeframe/13.0.782.215)'}


def get_html(url, useragent=None, proxy=None):
    response = requests.get(url, headers=useragent, proxies=proxy)
    return response.text


def get_ip(html):
    print('New proxy & User-Agent:')
    soup = BeautifulSoup(html, 'lxml')
    ip = soup.find('span', class_='ip').text.strip()
    ua = soup.find('span', class_='ip').find_next_sibling('span').text.strip()
    print(ip)
    print(ua)
    print('-------------------')


def test_connection_proxy(url_test, useragent=None, proxy=None):
    proxy = {'http': f'http://{proxy}'}

    try:
        html = get_html(url_test, useragent, proxy)
        get_ip(html)
    except Exception as e:
        print(e)


def test_connection_proxies(url_test, useragents_file, proxies_file):
    '''
    :param url_test: String. Example: 'http://sitespy.ru/my-ip'
    :param useragents_file: String. Example: 'useragents.txt'
    :param proxies_file: String. Example: 'proxies.txt'
    :return: None
    '''
    useragents = open(useragents_file).read().split('\n')
    proxies = open(proxies_file).read().split('\n')

    for i in range(10):
        useragent = {'User-Agent': choice(useragents)}
        proxy = {'http': 'http://{}'.format(choice(proxies))}
        try:
            html = get_html(url_test, useragent, proxy)
        except:
            continue
        time.sleep(uniform(3, 5))
        get_ip(html)


def get_current_datetime(delimiter_time):
    return datetime.datetime.now().strftime(f'%Y.%m.%d_%H{delimiter_time}%M{delimiter_time}%S')


def run_time(f):
    def wrap():
        print('Start...')
        start = datetime.datetime.now()
        f()
        end = datetime.datetime.now()
        print('End')
        print("Time: ", end - start)
    return wrap


if __name__ == '__main__':
    # test_connection_proxy(URL_TEST, useragent, PROXY)
    # test_connection_proxies(URL_TEST, 'useragents.txt', 'proxies.txt')

    print(get_current_datetime)