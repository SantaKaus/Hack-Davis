# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

import http.client

import pandas as pd
import numpy as np

import dateutil
import datetime
import time
from time import sleep
from random import randint

import re
import requests
import pickle

import json

# Selenium imports
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# Setting up chromedriver
options = Options()
options.headless = True
#driver = webdriver.Chrome(executable_path='/bin/chromedriver')
driver = webdriver.Chrome(options=options)

# go straight to most-recent pages
petitions_url = 'https://www.change.org/petitions?selected=popular_weekly' # up to 5084
driver.get(petitions_url)


def get_petition_urls(start):
    d = []
    petitions = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".col-xs-12.col-md-8.col-md-offset-2 [href]")))
    stop = start+10
    for p in petitions[start:stop]:
        d.append(p.get_attribute('href'))
    return d


def click_load_more():
    driver.find_element_by_css_selector('.btn.btn-big.btn-full.bg-brighter').click()

def open_list(limit):
    for i in range(0, limit):
        try:
            click_load_more()
        except NoSuchElementException:
            sleep(2)
        sleep(2)

def update_next10(dic, start):
    d = get_petition_urls(start)
    dic.extend(d)
    #return dic

def get1000(dic, limit):
    start = 4
    for i in range(0, limit):
        update_next10(dic, start)
        start += 10
    return start

#urls1000 = chunk_petition_urls(master, petitions_url, 1, 1000, 100)
urls1000 = []
limit = 55
open_list(limit)
get1000(urls1000, limit)


cleanr = re.compile("<.*?>")
def cleanhtml(raw_html, cleanr):
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

json_dictionary = {"petitions":[]}

for url in urls1000:   

    # visit url:
    driver.get(url)
    print("Processing url", url)
    # collect description from <p> tags
    description = ""
    p_tags = driver.find_elements_by_css_selector(".mbl.type-break-word.type-l.rte")
    for p in p_tags:
        description += p.get_attribute("innerHTML")

    # strip to HTML
    description = cleanhtml(description, cleanr)

    # data cleaning- if description is short forget about this petition
    if len(description) < 100:
        continue

    # collect title -- note: slow reloads can cause blank page-- sleep(0.1) to avoid but still continue if not
    try:
        title = driver.find_element_by_css_selector(".mtl.mbxxxl.xs-mts.xs-mbxs.petition-title").get_attribute("innerHTML")
    except NoSuchElementException:
        continue

    # needs to be tested
    #if title == "Deleted":
    #    print("omit deleted")
    #    continue

    # collect image url

    image_url = driver.find_element_by_css_selector(".sc-fzpmMD.fPcnhl").get_attribute("src")

    # define dictionary of petition data
    petition_dictionary = {}
    petition_dictionary["url"] = url
    petition_dictionary["title"] = title
    petition_dictionary["description"] = description
    petition_dictionary["image_url"] = image_url

    json_dictionary["petitions"].append(petition_dictionary)
    sleep(0.1)

with open("petitions500.json", "w") as outfile:
    json.dump(json_dictionary, outfile)