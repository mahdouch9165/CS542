import os
import random
import time

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException, \
    NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

# Webdriver code adapted from
# @misc{dong2024fnspid,
#       title={FNSPID: A Comprehensive Financial News Dataset in Time Series}, 
#       author={Zihan Dong and Xinyu Fan and Zhiyuan Peng},
#       year={2024},
#       eprint={2402.06698},
#       archivePrefix={arXiv},
#       primaryClass={q-fin.ST}
# }
def get_webdriver():
    user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/93.0.961.47 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    ]
    random_user_agent = random.choice(user_agents)
    options = Options()
    options.add_argument(f"user-agent={random_user_agent}")
    options.page_load_strategy = 'none'
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--headless")
    options.add_argument('--log-level=3')
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.cache.disk.enable", False)
    profile.set_preference("browser.cache.memory.enable", False)
    profile.set_preference("browser.cache.offline.enable", False)
    profile.set_preference("network.http.use-cache", False)
    options.profile = profile

    driver = webdriver.Chrome(options=options)
    return driver

def safe_find_element(driver, by, value):
    try:
        content = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((by, value))
        )
        return content
    except StaleElementReferenceException:
        time.sleep(2)
        content = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((by, value))
        )
        return content

def safe_click(driver, by, value):
    try:
        element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()
    except StaleElementReferenceException:
        time.sleep(2)
        element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()

# Station Info:
# Chicago - KMDW, Elev: 617.0 ft; Lat: 41.78417, Lon: -87.75528
# NYC - KNYC, Elev: 154.0 ft; Lat: 40.78333, Lon: -73.96667
# Miami - KMIA, Elev: 10.0 ft; Lat: 25.79056, Lon: -80.31639
# Austin - KAUS, Elev: 486.0 ft; Lat: 30.18304, Lon: -97.67987
def get_city_info():
    info = {
        "Chicago": {"station": "KMDW", "elev": 617.0, "lat": 41.78417, "lon": -87.75528},
        "NYC": {"station": "KNYC", "elev": 154.0, "lat": 40.78333, "lon": -73.96667},
        "Miami": {"station": "KMIA", "elev": 10.0, "lat": 25.79056, "lon": -80.31639},
        "Austin": {"station": "KAUS", "elev": 486.0, "lat": 30.18304, "lon": -97.67987}
    }
    return info

# Useful Functions
def F_to_C(F):
    return (F - 32) * 5.0/9.0

def C_to_F(C):
    return C * 9.0/5.0 + 32

# Data source 1:
# 1. NOAA Daily Aggregated Data (For sure - Daily model)
# Process:
# Expectation is for four stations to have a csv file for them under the data folder.
# The csv files should be called:
# KMDW_NOAA.csv, KNYC_NOAA.csv, KMIA_NOAA.csv, KAUS_NOAA.csv
# If they exist the code will read them and see which days are missing and then download the missing days from the NOAA API.
# If the files do not exist, the code will download all the data from the NOAA API.
def update_noaa_data():
    # print current working directory
    data_path = "./data"