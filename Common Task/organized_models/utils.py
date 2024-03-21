import os
import random
import time

import pandas as pd
import re

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, StaleElementReferenceException, \
    NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

# Webdriver code (get_webdriver, and safe_find_element) adapted from
# @misc{dong2024fnspid,
#       title={FNSPID: A Comprehensive Financial News Dataset in Time Series}, 
#       author={Zihan Dong and Xinyu Fan and Zhiyuan Peng},
#       year={2024},
#       eprint={2402.06698},
#       archivePrefix={arXiv},
#       primaryClass={q-fin.ST}
# }
# Remaining code is original work.
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

def daily_data_listing(driver):
    # Click on the "Single-Station Products" menu
    single_station_menu = safe_find_element(driver, By.ID, 'single')
    safe_click(driver, By.ID, 'single')

    # Wait for the menu to expand and be clickable
    daily_data_listing = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.ID, 'ui-id-4'))
    )
    safe_click(driver, By.ID, 'ui-id-4')

    # Select the output format
    csv_label = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, 'label[for="outopt_csv"]'))
    )
    csv_label = safe_find_element(driver, By.CSS_SELECTOR, 'label[for="outopt_csv"]')
    #safe_click(driver, By.CSS_SELECTOR, 'label[for="outopt_csv"]')
    driver.execute_script("arguments[0].click();", csv_label)
    
    # Click on the calendar icon to open the date range picker
    calendar_icon = safe_find_element(driver, By.ID, 'dp_calicon')
    safe_click(driver, By.ID, 'dp_calicon')
    return

def daily_data_listing_por(driver, symbol):
    url = "https://scacis.rcc-acis.org/"
    
    driver.get(url)
    
    # initial routine 
    daily_data_listing(driver)
    
    # Wait for the date range picker to be visible
    date_range_picker = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.ui-daterangepicker'))
    )

    # Click on the "Period of Record" option
    period_of_record = safe_find_element(driver, By.CSS_SELECTOR, '.ui-daterangepicker-PeriodofRecord')
    safe_click(driver, By.CSS_SELECTOR, '.ui-daterangepicker-PeriodofRecord')

    # Click on the checkboxes
    click_all_checkboxes(driver)

    # Put the symbol in the input box
    input_symbol(driver, symbol)

    # Click the "Go" button
    click_go(driver)

    # accept the pop up
    accept_pop_up(driver)

    csv_content = get_csv_content(driver)
    
    driver.quit()
    
    return csv_content

def daily_data_listing_7_day(driver, symbol):
    url = "https://scacis.rcc-acis.org/"
    
    driver.get(url)
    
    # initial routine 
    daily_data_listing(driver)
    
    # Wait for the date range picker to be visible
    date_range_picker = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.ui-daterangepicker'))
    )

    # Click on the "Period of Record" option
    period_of_record = safe_find_element(driver, By.CSS_SELECTOR, '.ui-daterangepicker-Last7Days')
    safe_click(driver, By.CSS_SELECTOR, '.ui-daterangepicker-Last7Days')

    # Click on the checkboxes
    click_all_checkboxes(driver)

    # Put the symbol in the input box
    input_symbol(driver, symbol)

    # Click the "Go" button
    click_go(driver)

    # accept the pop up
    accept_pop_up(driver)

    csv_content = get_csv_content(driver)
    
    driver.quit()
    
    return csv_content

def input_symbol(driver, symbol):
    # Assuming `station_select_menu` is the correct trigger element
    station_select_menu = safe_find_element(driver, By.ID, 'station_acc')
    driver.execute_script("arguments[0].click();", station_select_menu)
    
    # Wait for the station select input field to be visible (instead of just present)
    station_select = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.acis-idContainer input[type="text"]'))
    )

    # Clear the existing value and input the symbol
    station_select.clear()
    station_select.send_keys(symbol)

def click_all_checkboxes(driver):
    # Find all the checkboxes within the table
    checkboxes = driver.find_elements(By.CSS_SELECTOR, '.acis-multiInputTable input[type="checkbox"]')
    
    # Click each checkbox using JavaScript
    for checkbox in checkboxes:
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)

    time.sleep(2)  # Pause for 2 seconds to allow the checkboxes to be clicked

def click_go(driver):
    go_button = safe_find_element(driver, By.ID, 'go')
    safe_click(driver, By.ID, 'go')

def accept_pop_up(driver):
    try:
        # Wait for the alert to be present
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        
        # Switch to the alert and accept it
        alert = driver.switch_to.alert
        alert.accept()
        
        #print("Pop-up alert accepted.")
    except TimeoutException:
        # Handle the case where the alert does not appear within 5 seconds
        #print("No pop-up alert to accept.")
        # do nothing
        pass

def get_csv_content(driver):
    # Wait for the CSV data to be present in the results_area
    csv_data = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#results_area pre'))
    )

    # Get the text content of the <pre> element
    csv_content = csv_data.get_attribute('textContent')

    return csv_content

def process_daily_data_noaa_csv(csv_content):
    pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    corrected_content = re.sub(pattern, r'\n\1', csv_content)
    corrected_list = corrected_content.split('\n')
    
    # The first line has the clumn names and the title
    first_line = corrected_list.pop(0)
    column_names = first_line.split(', ')
    column_names.pop(0)
    # rename the first column name to 'Date'
    column_names[0] = 'Date'
    
    # The rest of the lines are the data
    data = []
    for line in corrected_list:
        data.append(line.split(', '))
        
    df = pd.DataFrame(data, columns=column_names)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # For other columns try to convert to numeric
    for column in df.columns[1:]:  # Skip the first column ('Date')
        df[column] = pd.to_numeric(df[column], errors='coerce')
    
    return df

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
    data_path = "./data"
    # Get city dict
    city_info = get_city_info()
    # city_list
    city_list = list(city_info.keys())
    # for each city in city_list, look in the data folder for the file
    for city in city_list:
        city_file = f"{data_path}/{city}_NOAA.csv"
        city_station_id = city_info[city]["station"]
        driver = get_webdriver()
        # if the file does not exist, download the noaa data
        csv_content = daily_data_listing_por(driver, city_station_id)
        df = process_daily_data_noaa_csv(csv_content)
        df.to_csv(city_file, index=False)
        # Ideally we would append the new data to the existing file, but for now we will overwrite it (does not take too long (4min))