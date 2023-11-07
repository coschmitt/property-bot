import json
import sys
import re
import ipdb
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import constants

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

def get_page_data(cards):
    page_json = []

    for card in cards:
        home_json = load_home_stats(card)
        loc_details, price_details = get_details_dict(card) # location stats
        home_json["name"] = loc_details['name']
        home_json["url"] = constants.BASE_URL + loc_details['url']
        home_json["address"] = {
            'street'  : loc_details['address']['streetAddress'],
            'state'   : loc_details['address']['addressLocality'],
            'zipcode' : loc_details['address']['postalCode'],
            'country' : loc_details['address']['addressCountry']
        }
        
        home_json["num_rooms"] = loc_details['numberOfRooms']
        home_json["type"] = loc_details['@type']
        home_json["price"] = float(price_details['offers']['price'])
        page_json.append(home_json)
    return page_json

def scrape():
    with webdriver.Chrome() as driver:
        driver.get("https://www.redfin.com/city/17151/CA/San-Francisco/filter/sort=lo-days")
        # paginate button
        next_btn = driver.find_element_by_xpath("//*[@id=\"results-display\"]/div[5]/div/div[3]/button[2]")
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
            
        with open("../page.json", "w") as f:
            f.write(json.dumps(home_json))
            
if __name__ == '__main__':
    scrape()
    

