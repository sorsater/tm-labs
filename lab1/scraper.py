'''
Created by micso554 and ludno249
'''

import sys
sys.path.append('..')

from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
from res.w8m8 import progressbar
import re

BASE_URL = 'https://play.google.com'

re_app = '<a href=\"(\/store\/apps\/details\?id=.*?)">'

def get_page(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup

def filter_out_description(content):
    description = content.find('div', {'class': 'show-more-content'})
    title = content.find('div', {'class': 'id-app-title'})
    return description.text, title.text

def find_app_from_url(url):
    page = get_page(url)
    urls = re.findall(re_app, str(page))

    return [BASE_URL + url + '&hl=en' for url in urls]

def find_all_apps(url, num_apps):
    apps = set(find_app_from_url(url))
    while len(apps) < num_apps:
        progressbar(len(apps) / num_apps)
        for app in apps:
            apps.update(find_app_from_url(app))
            progressbar(len(apps) / num_apps)
            if len(apps) >= num_apps:
                break

    return list(apps)[:num_apps]
