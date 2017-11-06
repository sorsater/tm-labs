

import sys
sys.path.append('..')

from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from res.w8m8 import progressbar
import re

BASE_URL = 'https://play.google.com'
SUPER_URL = 'https://play.google.com/store/apps'

NUM_APPS = 1000

re_app = '<a href=\"(\/store\/apps\/details\?id=.*?)">'

def get_page(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup

def filter_out_description(content):
    description = content.find('div', {'class': 'show-more-content'})

    return description.text

def find_app_from_url(url):
    page = get_page(url)
    urls = re.findall(re_app, str(page))

    return urls

def find_all_apps(url):
    apps = set()
    apps = set(find_app_from_url(url))
    while len(apps) < NUM_APPS:

        progressbar(len(apps) / NUM_APPS)

        for app in list(apps)[:]:
            apps.update(find_app_from_url(BASE_URL + app))
            
            progressbar(len(apps) / NUM_APPS)

            if len(apps) >= NUM_APPS:
                break
    return apps

if __name__ == '__main__':
    print('Finding {} apps'.format(NUM_APPS))        
    apps = find_all_apps(SUPER_URL)
    print('\033[KFound {} apps'.format(len(apps)))