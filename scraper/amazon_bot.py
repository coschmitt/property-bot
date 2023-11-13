import json
import sys
import re
import ipdb
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection

import constants
import os

def scrape():
    AUTH = os.environ['AUTH']
    HOST = os.environ['HOST']
    SBR_WEBDRIVER = f'https://{AUTH}@{HOST}'
    chrome_options = webdriver.ChromeOptions()
    prefs = {
         "profile.managed_default_content_settings.images":2,
         "profile.default_content_setting_values.notifications":2,
         "profile.managed_default_content_settings.stylesheets":2,
         "profile.managed_default_content_settings.cookies":2,
         "profile.managed_default_content_settings.plugins":1,
         "profile.managed_default_content_settings.popups":2,
         "profile.managed_default_content_settings.geolocation":2,
         "profile.managed_default_content_settings.media_stream":2,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    #with Remote(sbr_connection, options=chrome_options) as driver:
    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get("https://www.amazon.com/Best-Sellers-Sports-Outdoors/zgbs/sporting-goods/ref=zg_bs_nav_sporting-goods_0")
        driver.find_element(By.CLASS_NAME, "a-last")


if __name__ == '__main__':
    scrape()
    