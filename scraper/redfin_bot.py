import json
import re
import ipdb
from bs4 import BeautifulSoup
import os
import requests
import boto3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection

import constants

def batched(iterable: list, max_batch_size: int):
    batch = []
    for element in iterable:
        batch.append(element)
        if len(batch) >= max_batch_size:
            yield batch
            batch = []
    if len(batch) > 0:
        yield batch

def load_home_stats(card):
    stats = card.find("div", {"class": "HomeStatsV2"}).find_all("div", {"class": "stats"})
    stat_json = {'stats': {}}
    for stat in stats:
        contents = " ".join(stat.findAll(string=True, recursive=False))

        if contents == None or not any(chr.isdigit() for chr in contents): # filters out stats that aren't filed in (ex. "- rooms")
            continue

        num = contents.split(" ")[0].replace(",", "")
        if "beds" in contents.lower():
            stat_json["stats"]["beds"] = float(num)
        elif "baths" in contents.lower():
            stat_json["stats"]["baths"] = float(num)
        elif "lot" in contents.lower():
            stat_json["stats"]["lot_sqft"] = float(num)
        elif "sq ft" in contents.lower():
            stat_json["stats"]["home_sqft"] = float(num)
        
    return stat_json

def get_details_dict(card):
    scripts = card.find_all("script")
    return json.loads(scripts[0].contents[0])

def get_key(address):
    return "".join(address["street"].split()) + "$" + address["zipcode"]

def get_page_data(cards):
    page_json = []

    for card in cards:
        # home_json = load_home_stats(card)
        home_json = {}
        loc_details, price_details = get_details_dict(card) # location stats
        home_json["name"] = loc_details['name']
        home_json["url"] = constants.BASE_URL + loc_details['url']
        home_json["address"] = {
            'street'  : loc_details['address']['streetAddress'],
            'city'    : loc_details['address']['addressLocality'],
            'zipcode' : loc_details['address']['postalCode'],
            'state'   : loc_details['address']['addressRegion'],
            'country' : loc_details['address']['addressCountry']
        }
        
        home_json["num_rooms"] = loc_details.get("numberOfRooms", None)
        home_json["type"] = loc_details['@type']

        # if this fails, then we are going to skip the house
        try:
            home_json["price"] = float(price_details['offers']['price'])
        except:
            continue

        page_json.append(home_json)
    return page_json

def save_data(home_json):
    name_set = set()
    sqs = boto3.resource("sqs", region_name = "us-east-2")
    queue = sqs.get_queue_by_name(QueueName="property-bot-queue")
    
    for batch in batched(home_json, 10):
        entries = []
        for body in batch:
            key = get_key(body["address"])
            if key not in name_set:
                entries.append({
                    'MessageBody': json.dumps(body),
                    'Id': str(hash(body["name"]))
                })
                name_set.add(key)
        response = queue.send_messages(Entries=entries)

"""
    Selenium Scraper: perfect for local development since we can easily paginate and its fast. Will not work in AWS or Azure 
    without a residential proxy.
"""
def scrape():
    chrome_options = webdriver.ChromeOptions()
    PROXY = "http://36b742020a7664a713823b81768ddb9fb5ee54d1:premium_proxy=true&proxy_country=us@proxy.zenrows.com:8001"
    chrome_options.add_argument(f"--proxy-server={PROXY}")
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

    # with Remote(sbr_connection, options=chrome_options) as driver:
    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get("https://www.redfin.com/city/17151/CA/San-Francisco/filter/sort=lo-days")
        # paginate button
        next_btn = driver.find_element(By.XPATH, "//*[@id=\"results-display\"]/div[5]/div/div[3]/button[2]")
        home_json = []
        for _ in range (constants.NUM_PAGES):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # get all the cards that have housing data
            cards = soup.find("div", {"class": "HomeViews"}).find_all('div', {'id': re.compile(r'^MapHomeCard_\d*$')})
            # iterate through cards and get stats
            home_json.extend(get_page_data(cards))
            # go to next page, if we can't then break the loop
            try:
                driver.execute_script("arguments[0].click();", next_btn)
            except:
                break

        save_data(home_json)
        # with open("../page.json", "w") as f:
        #     f.write(json.dumps(home_json))

"""
    Scraping Ant solution: Use this method when running scraper from cloud. Most likely IPs coming from AWS or Azure 
    will be blocked. Scraping Ant provides Residential proxies to avoid this (for a cost...)
"""
def get_source_html():
    url = "https://api.scrapingant.com/v2/general"
    params = {
        "url": "https://www.redfin.com/city/17151/CA/San-Francisco/filter/sort=lo-days",
        "x-api-key": os.environ["SCRAPING_ANT_KEY"],
        "proxy_type": "residential"

    }

    r = requests.get(url, params=params)
    return r.text

def scraping_ant():
    page_source = get_source_html()
    soup = BeautifulSoup(page_source, 'html.parser')
    # get all the cards that have housing data
    cards = soup.find("div", {"class": "HomeViews"}).find_all('div', {'id': re.compile(r'^MapHomeCard_\d*$')})
    # iterate through cards and get stats
    home_json = get_page_data(cards)

    with open("../page.json", "w") as f:
        f.write(json.dumps(home_json))
            
if __name__ == '__main__':
    scrape()
    

