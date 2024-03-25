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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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
    options.set_capability("goog:loggingPrefs", {
        'performance': 'ALL',
        'browser': 'ALL'
    })
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
    # Austin
    noaa_austin_path = './data/Austin_NOAA.csv'
    om_austin_path = './data/Austin_OM.csv'
    wrh_austin_path = './data/Austin_WRH.csv'
    air_austin_path = './data/Austin_Air_Quality.csv'
    solar_austin_path = './data/Austin_Solar_Soil.csv'
    attn_lstm_autin_path = './models/weights/Austin_attn_lstm.pt'
    lstm_austin_path = './models/weights/Austin_lstm.pt'
    scaler_austin_path = './models/weights/Austin_scaler_features.pkl'
    # NYC
    noaa_nyc_path = './data/NYC_NOAA.csv'
    om_nyc_path = './data/NYC_OM.csv'
    wrh_nyc_path = './data/NYC_WRH.csv'
    air_nyc_path = './data/NYC_Air_Quality.csv'
    solar_nyc_path = './data/NYC_Solar_Soil.csv'
    attn_nyc_path = './models/weights/NYC_attn_lstm.pt'
    lstm_nyc_path = './models/weights/NYC_lstm.pt'
    scaler_nyc_path = './models/weights/NYC_scaler_features.pkl'
    # Miami
    noaa_miami_path = './data/Miami_NOAA.csv'
    om_miami_path = './data/Miami_OM.csv'
    wrh_miami_path = './data/Miami_WRH.csv'
    air_miami_path = './data/Miami_Air_Quality.csv'
    solar_miami_path = './data/Miami_Solar_Soil.csv'
    attn_lstm_miami_path = './models/weights/Miami_attn_lstm.pt'
    lstm_miami_path = './models/weights/Miami_lstm.pt'
    scaler_miami_path = './models/weights/Miami_scaler_features.pkl'
    # Chicago
    noaa_chicago_path = './data/Chicago_NOAA.csv'
    om_chicago_path = './data/Chicago_OM.csv'
    wrh_chicago_path = './data/Chicago_WRH.csv'
    air_chicago_path = './data/Chicago_Air_Quality.csv'
    solar_chicago_path = './data/Chicago_Solar_Soil.csv'   
    attn_lstm_chicago_path = './models/weights/Chicago_attn_lstm.pt'
    lstm_chicago_path = './models/weights/Chicago_lstm.pt'
    scaler_chicago_path = './models/weights/Chicago_scaler_features.pkl'
    
    info = {
        "Chicago": {
            "station": "KMDW", 
            "elev": 617.0, 
            "lat": 41.78417, 
            "lon": -87.75528, 
            "tz": "America/Chicago",
            "noaa": noaa_chicago_path,
            "om": om_chicago_path,
            "wrh": wrh_chicago_path,
            "aq": air_chicago_path,
            "ss": solar_chicago_path,
            "attn_lstm": attn_lstm_chicago_path,
            "lstm": lstm_chicago_path,
            "scaler": scaler_chicago_path},
        "NYC": {
            "station": "KNYC",
            "elev": 154.0,
            "lat": 40.78333,
            "lon": -73.96667,
            "tz": "America/New_York",
            "noaa": noaa_nyc_path,
            "om": om_nyc_path,
            "wrh": wrh_nyc_path,
            "aq": air_nyc_path,
            "ss": solar_nyc_path,
            "attn_lstm": attn_nyc_path,
            "lstm": lstm_nyc_path,
            "scaler": scaler_nyc_path},
        "Miami": {
            "station": "KMIA", 
            "elev": 10.0, 
            "lat": 25.79056, 
            "lon": -80.31639, 
            "tz": "America/New_York",
            "noaa": noaa_miami_path,
            "om": om_miami_path,
            "wrh": wrh_miami_path,
            "aq": air_miami_path,
            "ss": solar_miami_path,
            "attn_lstm": attn_lstm_miami_path,
            "lstm": lstm_miami_path,
            "scaler": scaler_miami_path},
        "Austin": {
            "station": "KAUS", 
            "elev": 486.0, 
            "lat": 30.18304, 
            "lon": -97.67987, 
            "tz": "America/Chicago",
            "noaa": noaa_austin_path,
            "om": om_austin_path,
            "wrh": wrh_austin_path,
            "aq": air_austin_path,
            "ss": solar_austin_path,
            "attn_lstm": attn_lstm_autin_path,
            "lstm": lstm_austin_path,
            "scaler": scaler_austin_path}
    }
    return info

def get_time_zone(city):
    city_info = get_city_info()
    return city_info[city]["tz"]

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
# If they exist tshe code will read them and see which days are missing and then download the missing days from the NOAA API.
# If the files do not exist, the code will download all the data from the NOAA API.
def load_NOAA_data():
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
        csv_historic_content = daily_data_listing_por(driver, city_station_id)
        df = process_daily_data_noaa_csv(csv_historic_content)
        driver = get_webdriver()
        csv_new_content = daily_data_listing_7_day(driver, city_station_id)
        df_new = process_daily_data_noaa_csv(csv_new_content)
        # Add the last row of the new data to the historic data
        df = pd.concat([df, df_new.tail(1)], ignore_index=True)
        df.to_csv(city_file, index=False)
        # Ideally we would append the new data to the existing file, but for now we will overwrite it (does not take too long (4min))
        
# Data source 2:
# OpenMeteo
# Will be used to fill in the gaps in the NOAA data

def update_NOAA_data():
    data_path = "./data"
    # Get city dict
    city_info = get_city_info()
    # city_list
    city_list = list(city_info.keys())
    for city in city_list:
        city_file = f"{data_path}/{city}_NOAA.csv"
        city_station_id = city_info[city]["station"]
        driver = get_webdriver()
        csv_new_content = daily_data_listing_7_day(driver, city_station_id)
        df_new = process_daily_data_noaa_csv(csv_new_content)
        old_df = pd.read_csv(city_file)
        old_df['Date'] = pd.to_datetime(old_df['Date'])  # Convert 'Date' to datetime
        last_date = old_df['Date'].iloc[-1]
        new_df = df_new[df_new['Date'] > last_date]
        today = pd.to_datetime("now").date().strftime("%Y-%m-%d")
        new_df = new_df[new_df['Date'] < today]
        new_df['Date'] = pd.to_datetime(new_df['Date'])  # Convert 'Date' to datetime
        df = pd.concat([old_df, new_df], ignore_index=True)
        df.to_csv(city_file, index=False)

import openmeteo_requests
import requests_cache
from retry_requests import retry

def load_OM_data():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    
    def get_historical_data(latitude, longitude, start_date, end_date):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum", "et0_fao_evapotranspiration"],
            "temperature_unit": "fahrenheit"
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
        daily_apparent_temperature_min = daily.Variables(4).ValuesAsNumpy()
        daily_sunrise = daily.Variables(5).ValuesAsNumpy()
        daily_sunset = daily.Variables(6).ValuesAsNumpy()
        daily_daylight_duration = daily.Variables(7).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(8).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(9).ValuesAsNumpy()
        daily_rain_sum = daily.Variables(10).ValuesAsNumpy()
        daily_snowfall_sum = daily.Variables(11).ValuesAsNumpy()
        daily_precipitation_hours = daily.Variables(12).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(13).ValuesAsNumpy()
        daily_wind_gusts_10m_max = daily.Variables(14).ValuesAsNumpy()
        daily_wind_direction_10m_dominant = daily.Variables(15).ValuesAsNumpy()
        daily_shortwave_radiation_sum = daily.Variables(16).ValuesAsNumpy()
        daily_et0_fao_evapotranspiration = daily.Variables(17).ValuesAsNumpy()
        
        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
        daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
        daily_data["sunrise"] = daily_sunrise
        daily_data["sunset"] = daily_sunset
        daily_data["daylight_duration"] = daily_daylight_duration
        daily_data["sunshine_duration"] = daily_sunshine_duration
        daily_data["precipitation_sum"] = daily_precipitation_sum
        daily_data["rain_sum"] = daily_rain_sum
        daily_data["snowfall_sum"] = daily_snowfall_sum
        daily_data["precipitation_hours"] = daily_precipitation_hours
        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
        daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
        daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
        daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum
        daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration
        
        return pd.DataFrame(data=daily_data)

    def get_forecast_data(latitude, longitude):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m",
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum", "et0_fao_evapotranspiration"],
            "temperature_unit": "fahrenheit",
            "past_days": 1,
            "forecast_days": 0
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        
        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
        daily_apparent_temperature_min = daily.Variables(4).ValuesAsNumpy()
        daily_sunrise = daily.Variables(5).ValuesAsNumpy()
        daily_sunset = daily.Variables(6).ValuesAsNumpy()
        daily_daylight_duration = daily.Variables(7).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(8).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(9).ValuesAsNumpy()
        daily_rain_sum = daily.Variables(10).ValuesAsNumpy()
        daily_snowfall_sum = daily.Variables(11).ValuesAsNumpy()
        daily_precipitation_hours = daily.Variables(12).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(13).ValuesAsNumpy()
        daily_wind_gusts_10m_max = daily.Variables(14).ValuesAsNumpy()
        daily_wind_direction_10m_dominant = daily.Variables(15).ValuesAsNumpy()
        daily_shortwave_radiation_sum = daily.Variables(16).ValuesAsNumpy()
        daily_et0_fao_evapotranspiration = daily.Variables(17).ValuesAsNumpy()
        
        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
        daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
        daily_data["sunrise"] = daily_sunrise
        daily_data["sunset"] = daily_sunset
        daily_data["daylight_duration"] = daily_daylight_duration
        daily_data["sunshine_duration"] = daily_sunshine_duration
        daily_data["precipitation_sum"] = daily_precipitation_sum
        daily_data["rain_sum"] = daily_rain_sum
        daily_data["snowfall_sum"] = daily_snowfall_sum
        daily_data["precipitation_hours"] = daily_precipitation_hours
        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
        daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
        daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
        daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum
        daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration
        
        daily_dataframe = pd.DataFrame(data=daily_data)
        
        return hourly_dataframe, daily_dataframe

    # Example usage
    data_path = "./data"
    # Get city dict
    city_info = get_city_info()
    # city_list
    city_list = list(city_info.keys())
    
    for city in city_list:
        city_file = f"{data_path}/{city}_OM.csv"
        latitude = city_info[city]["lat"]
        longitude = city_info[city]["lon"]
        start_date = "1940-01-01"
        end_date = pd.to_datetime("now") - pd.Timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")

        historical_data = get_historical_data(latitude, longitude, start_date, end_date)
        
        time.sleep(60)
        
        forecast_hourly_data, forecast_daily_data = get_forecast_data(latitude, longitude)
        
        combined_daily_data = pd.concat([historical_data, forecast_daily_data], ignore_index=True)

        combined_daily_data.to_csv(city_file, index=False)
        
        time.sleep(60)            

def update_OM_data():
        # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    
    def get_historical_data(latitude, longitude, start_date, end_date):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum", "et0_fao_evapotranspiration"],
            "temperature_unit": "fahrenheit"
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
        daily_apparent_temperature_min = daily.Variables(4).ValuesAsNumpy()
        daily_sunrise = daily.Variables(5).ValuesAsNumpy()
        daily_sunset = daily.Variables(6).ValuesAsNumpy()
        daily_daylight_duration = daily.Variables(7).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(8).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(9).ValuesAsNumpy()
        daily_rain_sum = daily.Variables(10).ValuesAsNumpy()
        daily_snowfall_sum = daily.Variables(11).ValuesAsNumpy()
        daily_precipitation_hours = daily.Variables(12).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(13).ValuesAsNumpy()
        daily_wind_gusts_10m_max = daily.Variables(14).ValuesAsNumpy()
        daily_wind_direction_10m_dominant = daily.Variables(15).ValuesAsNumpy()
        daily_shortwave_radiation_sum = daily.Variables(16).ValuesAsNumpy()
        daily_et0_fao_evapotranspiration = daily.Variables(17).ValuesAsNumpy()
        
        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
        daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
        daily_data["sunrise"] = daily_sunrise
        daily_data["sunset"] = daily_sunset
        daily_data["daylight_duration"] = daily_daylight_duration
        daily_data["sunshine_duration"] = daily_sunshine_duration
        daily_data["precipitation_sum"] = daily_precipitation_sum
        daily_data["rain_sum"] = daily_rain_sum
        daily_data["snowfall_sum"] = daily_snowfall_sum
        daily_data["precipitation_hours"] = daily_precipitation_hours
        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
        daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
        daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
        daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum
        daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration
        
        return pd.DataFrame(data=daily_data)

    def get_forecast_data(latitude, longitude):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m",
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "apparent_temperature_max", "apparent_temperature_min", "sunrise", "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum", "et0_fao_evapotranspiration"],
            "temperature_unit": "fahrenheit",
            "past_days": 1,
            "forecast_days": 0
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        
        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
        daily_apparent_temperature_min = daily.Variables(4).ValuesAsNumpy()
        daily_sunrise = daily.Variables(5).ValuesAsNumpy()
        daily_sunset = daily.Variables(6).ValuesAsNumpy()
        daily_daylight_duration = daily.Variables(7).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(8).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(9).ValuesAsNumpy()
        daily_rain_sum = daily.Variables(10).ValuesAsNumpy()
        daily_snowfall_sum = daily.Variables(11).ValuesAsNumpy()
        daily_precipitation_hours = daily.Variables(12).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(13).ValuesAsNumpy()
        daily_wind_gusts_10m_max = daily.Variables(14).ValuesAsNumpy()
        daily_wind_direction_10m_dominant = daily.Variables(15).ValuesAsNumpy()
        daily_shortwave_radiation_sum = daily.Variables(16).ValuesAsNumpy()
        daily_et0_fao_evapotranspiration = daily.Variables(17).ValuesAsNumpy()
        
        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        )}
        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
        daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
        daily_data["sunrise"] = daily_sunrise
        daily_data["sunset"] = daily_sunset
        daily_data["daylight_duration"] = daily_daylight_duration
        daily_data["sunshine_duration"] = daily_sunshine_duration
        daily_data["precipitation_sum"] = daily_precipitation_sum
        daily_data["rain_sum"] = daily_rain_sum
        daily_data["snowfall_sum"] = daily_snowfall_sum
        daily_data["precipitation_hours"] = daily_precipitation_hours
        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
        daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
        daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
        daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum
        daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration
        
        daily_dataframe = pd.DataFrame(data=daily_data)
        
        return hourly_dataframe, daily_dataframe

    # Example usage
    data_path = "./data"
    # Get city dict
    city_info = get_city_info()
    # city_list
    city_list = list(city_info.keys())
    
    for city in city_list:
        city_file = f"{data_path}/{city}_OM.csv"
        latitude = city_info[city]["lat"]
        longitude = city_info[city]["lon"]
        
        old_df = pd.read_csv(city_file)
        old_df['date'] = pd.to_datetime(old_df['date'])
        last_date = old_df['date'].iloc[-1]
        
        start_date = last_date + pd.Timedelta(days=1)
        start_date = start_date.strftime("%Y-%m-%d")
        
        end_date = pd.to_datetime("now") - pd.Timedelta(days=1)
        end_date = end_date.strftime("%Y-%m-%d")
        
        if start_date == end_date:
            forecast_hourly_data, combined_daily_data = get_forecast_data(latitude, longitude)
        else:
            historical_data = get_historical_data(latitude, longitude, start_date, end_date)
        
            time.sleep(60)
            
            forecast_hourly_data, forecast_daily_data = get_forecast_data(latitude, longitude)
            
            combined_daily_data = pd.concat([historical_data, forecast_daily_data], ignore_index=True)        
        
        combined_daily_data = pd.concat([old_df, combined_daily_data], ignore_index=True)
            
        combined_daily_data.to_csv(city_file, index=False)
                
        time.sleep(30)
        
from meteostat import Stations, Daily
from datetime import datetime

def load_MS_data():
    city_info = get_city_info()
    start = datetime(1869,1,1)
    end = datetime(2024,3,20)

    for key in city_info.keys():
        city = city_info[key]
        station_id = city['station']
        lat = city['lat']
        lon = city['lon']
        elev = city['elev']
        
        stations = Stations()
        nearby = stations.nearby(lat, lon)
        nearest = nearby.fetch(1)
        sid = nearest.index[0]
        
        data = Daily(sid, start, end)
        data = data.fetch()
        
        # save data
        data.to_csv(f'../data/{key}_MS.csv')

import json
import requests
        
def load_WRH_data():
    data_path = "./data"
    # Get city dict
    city_info = get_city_info()
    # city_list
    city_list = list(city_info.keys())
    for city in city_list:
        city_file = f"{data_path}/{city}_WRH.csv"
        city_station_id = city_info[city]["station"]
        url = f"https://www.weather.gov/wrh/timeseries?site={city_station_id}"
        driver = get_webdriver()
        driver.get(url)
        time.sleep(15)
        logs = driver.get_log('performance')
        urls = []
        for entry in logs:
            message = entry['message']
            if 'token' in message.lower():
                entry = json.loads(message)
                try:
                    url = entry['message']['params']['request']['url']
                except:
                    continue
                urls.append(url)
        # extract the token from the url
        token = urls[0].split('token=')[1].split('&')[0]
        start = '200207140000'
        # end date is today
        end = pd.to_datetime("now").strftime("%Y%m%d%H%M")
        url_form = f'https://api.mesowest.net/v2/stations/timeseries?STID={city_station_id}&showemptystations=1&units=temp|F,speed|mph,english&start={start}&end={end}&token={token}&complete=1&obtimezone=local'
        response = requests.get(url_form)
        data = response.json()
        observations = data['STATION'][0]['OBSERVATIONS']
        df = pd.DataFrame(observations)
        df.to_csv(city_file, index=False)
        driver.quit()
        
def update_WRH_data():
    data_path = "./data"
    # Get city dict
    city_info = get_city_info()
    # city_list
    city_list = list(city_info.keys())
    for city in city_list:
        city_file = f"{data_path}/{city}_WRH.csv"
        city_station_id = city_info[city]["station"]
        url = f"https://www.weather.gov/wrh/timeseries?site={city_station_id}"
        driver = get_webdriver()
        driver.get(url)
        time.sleep(15)
        logs = driver.get_log('performance')
        urls = []
        for entry in logs:
            message = entry['message']
            if 'token' in message.lower():
                entry = json.loads(message)
                try:
                    url = entry['message']['params']['request']['url']
                except:
                    continue
                urls.append(url)
        # extract the token from the url
        token = urls[0].split('token=')[1].split('&')[0]
        # Load the existing data
        old_df = pd.read_csv(city_file)
        old_df['date_time'] = pd.to_datetime(old_df['date_time'])
        start = old_df['date_time'].iloc[-1].strftime("%Y%m%d") + '0000'
        # end date is today
        end = pd.to_datetime("now").strftime("%Y%m%d%H%M")
        url_form = f'https://api.mesowest.net/v2/stations/timeseries?STID={city_station_id}&showemptystations=1&units=temp|F,speed|mph,english&start={start}&end={end}&token={token}&complete=1&obtimezone=local'
        response = requests.get(url_form)
        data = response.json()
        observations = data['STATION'][0]['OBSERVATIONS']
        df = pd.DataFrame(observations)
        df['date_time'] = pd.to_datetime(df['date_time'])
        last_date = old_df['date_time'].iloc[-1]
        new_df = df[df['date_time'] > last_date]
        # new_df must not include today's data (only compare the date part)
        today = pd.to_datetime("now").date()
        new_df = new_df[new_df['date_time'].dt.date < today]        
        new_df = pd.concat([old_df, new_df], ignore_index=True)   
        new_df.to_csv(city_file, index=False)
        driver.quit()
        
def get_Solar_Soil_data():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    
    url = "https://archive-api.open-meteo.com/v1/archive"

    def get_historical_data(lat, long, start, end, tz):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": long,
            "start_date": start,
            "end_date": end,
            "hourly": ["soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm", "soil_temperature_28_to_100cm", "soil_temperature_100_to_255cm", "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm", "soil_moisture_28_to_100cm", "soil_moisture_100_to_255cm", "shortwave_radiation", "direct_radiation", "diffuse_radiation", "direct_normal_irradiance", "global_tilted_irradiance", "terrestrial_radiation", "shortwave_radiation_instant", "direct_radiation_instant", "diffuse_radiation_instant", "direct_normal_irradiance_instant", "global_tilted_irradiance_instant", "terrestrial_radiation_instant"],
            "timezone": tz
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_soil_temperature_0_to_7cm = hourly.Variables(0).ValuesAsNumpy()
        hourly_soil_temperature_7_to_28cm = hourly.Variables(1).ValuesAsNumpy()
        hourly_soil_temperature_28_to_100cm = hourly.Variables(2).ValuesAsNumpy()
        hourly_soil_temperature_100_to_255cm = hourly.Variables(3).ValuesAsNumpy()
        hourly_soil_moisture_0_to_7cm = hourly.Variables(4).ValuesAsNumpy()
        hourly_soil_moisture_7_to_28cm = hourly.Variables(5).ValuesAsNumpy()
        hourly_soil_moisture_28_to_100cm = hourly.Variables(6).ValuesAsNumpy()
        hourly_soil_moisture_100_to_255cm = hourly.Variables(7).ValuesAsNumpy()
        hourly_shortwave_radiation = hourly.Variables(8).ValuesAsNumpy()
        hourly_direct_radiation = hourly.Variables(9).ValuesAsNumpy()
        hourly_diffuse_radiation = hourly.Variables(10).ValuesAsNumpy()
        hourly_direct_normal_irradiance = hourly.Variables(11).ValuesAsNumpy()
        hourly_global_tilted_irradiance = hourly.Variables(12).ValuesAsNumpy()
        hourly_terrestrial_radiation = hourly.Variables(13).ValuesAsNumpy()
        hourly_shortwave_radiation_instant = hourly.Variables(14).ValuesAsNumpy()
        hourly_direct_radiation_instant = hourly.Variables(15).ValuesAsNumpy()
        hourly_diffuse_radiation_instant = hourly.Variables(16).ValuesAsNumpy()
        hourly_direct_normal_irradiance_instant = hourly.Variables(17).ValuesAsNumpy()
        hourly_global_tilted_irradiance_instant = hourly.Variables(18).ValuesAsNumpy()
        hourly_terrestrial_radiation_instant = hourly.Variables(19).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["soil_temperature_0_to_7cm"] = hourly_soil_temperature_0_to_7cm
        hourly_data["soil_temperature_7_to_28cm"] = hourly_soil_temperature_7_to_28cm
        hourly_data["soil_temperature_28_to_100cm"] = hourly_soil_temperature_28_to_100cm
        hourly_data["soil_temperature_100_to_255cm"] = hourly_soil_temperature_100_to_255cm
        hourly_data["soil_moisture_0_to_7cm"] = hourly_soil_moisture_0_to_7cm
        hourly_data["soil_moisture_7_to_28cm"] = hourly_soil_moisture_7_to_28cm
        hourly_data["soil_moisture_28_to_100cm"] = hourly_soil_moisture_28_to_100cm
        hourly_data["soil_moisture_100_to_255cm"] = hourly_soil_moisture_100_to_255cm
        hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
        hourly_data["direct_radiation"] = hourly_direct_radiation
        hourly_data["diffuse_radiation"] = hourly_diffuse_radiation
        hourly_data["direct_normal_irradiance"] = hourly_direct_normal_irradiance
        hourly_data["global_tilted_irradiance"] = hourly_global_tilted_irradiance
        hourly_data["terrestrial_radiation"] = hourly_terrestrial_radiation
        hourly_data["shortwave_radiation_instant"] = hourly_shortwave_radiation_instant
        hourly_data["direct_radiation_instant"] = hourly_direct_radiation_instant
        hourly_data["diffuse_radiation_instant"] = hourly_diffuse_radiation_instant
        hourly_data["direct_normal_irradiance_instant"] = hourly_direct_normal_irradiance_instant
        hourly_data["global_tilted_irradiance_instant"] = hourly_global_tilted_irradiance_instant
        hourly_data["terrestrial_radiation_instant"] = hourly_terrestrial_radiation_instant

        hourly_dataframe = pd.DataFrame(data = hourly_data)
        return hourly_dataframe

    # Get city dict
    city_info = get_city_info()
    
    # city_list
    city_list = list(city_info.keys())
    
    for city in city_list:
        city_file = f"./data/{city}_Solar_Soil.csv"
        latitude = city_info[city]["lat"]
        longitude = city_info[city]["lon"]
        timezone = get_time_zone(city)
        start_date = "2002-08-14"
        end_date = pd.to_datetime("now") - pd.Timedelta(days = 1)
        end_date = end_date.strftime("%Y-%m-%d")
        df = get_historical_data(latitude, longitude, start_date, end_date, timezone)
        df.to_csv(city_file, index = False)
        time.sleep(60)
        
def get_Air_Quality_data():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    def get_historical_data(lat, long, start, end, tz):
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": lat,
            "longitude": long,
            "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "aerosol_optical_depth", "dust", "uv_index", "uv_index_clear_sky", "ammonia", "alder_pollen", "birch_pollen", "grass_pollen", "mugwort_pollen", "olive_pollen", "ragweed_pollen", "us_aqi", "us_aqi_pm2_5", "us_aqi_pm10", "us_aqi_nitrogen_dioxide", "us_aqi_carbon_monoxide", "us_aqi_ozone", "us_aqi_sulphur_dioxide"],
            "start_date": start,
            "end_date": end,
            "timezone": tz
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
        hourly_pm2_5 = hourly.Variables(1).ValuesAsNumpy()
        hourly_carbon_monoxide = hourly.Variables(2).ValuesAsNumpy()
        hourly_nitrogen_dioxide = hourly.Variables(3).ValuesAsNumpy()
        hourly_sulphur_dioxide = hourly.Variables(4).ValuesAsNumpy()
        hourly_ozone = hourly.Variables(5).ValuesAsNumpy()
        hourly_aerosol_optical_depth = hourly.Variables(6).ValuesAsNumpy()
        hourly_dust = hourly.Variables(7).ValuesAsNumpy()
        hourly_uv_index = hourly.Variables(8).ValuesAsNumpy()
        hourly_uv_index_clear_sky = hourly.Variables(9).ValuesAsNumpy()
        hourly_ammonia = hourly.Variables(10).ValuesAsNumpy()
        hourly_alder_pollen = hourly.Variables(11).ValuesAsNumpy()
        hourly_birch_pollen = hourly.Variables(12).ValuesAsNumpy()
        hourly_grass_pollen = hourly.Variables(13).ValuesAsNumpy()
        hourly_mugwort_pollen = hourly.Variables(14).ValuesAsNumpy()
        hourly_olive_pollen = hourly.Variables(15).ValuesAsNumpy()
        hourly_ragweed_pollen = hourly.Variables(16).ValuesAsNumpy()
        hourly_us_aqi = hourly.Variables(17).ValuesAsNumpy()
        hourly_us_aqi_pm2_5 = hourly.Variables(18).ValuesAsNumpy()
        hourly_us_aqi_pm10 = hourly.Variables(19).ValuesAsNumpy()
        hourly_us_aqi_nitrogen_dioxide = hourly.Variables(20).ValuesAsNumpy()
        hourly_us_aqi_carbon_monoxide = hourly.Variables(21).ValuesAsNumpy()
        hourly_us_aqi_ozone = hourly.Variables(22).ValuesAsNumpy()
        hourly_us_aqi_sulphur_dioxide = hourly.Variables(23).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["pm10"] = hourly_pm10
        hourly_data["pm2_5"] = hourly_pm2_5
        hourly_data["carbon_monoxide"] = hourly_carbon_monoxide
        hourly_data["nitrogen_dioxide"] = hourly_nitrogen_dioxide
        hourly_data["sulphur_dioxide"] = hourly_sulphur_dioxide
        hourly_data["ozone"] = hourly_ozone
        hourly_data["aerosol_optical_depth"] = hourly_aerosol_optical_depth
        hourly_data["dust"] = hourly_dust
        hourly_data["uv_index"] = hourly_uv_index
        hourly_data["uv_index_clear_sky"] = hourly_uv_index_clear_sky
        hourly_data["ammonia"] = hourly_ammonia
        hourly_data["alder_pollen"] = hourly_alder_pollen
        hourly_data["birch_pollen"] = hourly_birch_pollen
        hourly_data["grass_pollen"] = hourly_grass_pollen
        hourly_data["mugwort_pollen"] = hourly_mugwort_pollen
        hourly_data["olive_pollen"] = hourly_olive_pollen
        hourly_data["ragweed_pollen"] = hourly_ragweed_pollen
        hourly_data["us_aqi"] = hourly_us_aqi
        hourly_data["us_aqi_pm2_5"] = hourly_us_aqi_pm2_5
        hourly_data["us_aqi_pm10"] = hourly_us_aqi_pm10
        hourly_data["us_aqi_nitrogen_dioxide"] = hourly_us_aqi_nitrogen_dioxide
        hourly_data["us_aqi_carbon_monoxide"] = hourly_us_aqi_carbon_monoxide
        hourly_data["us_aqi_ozone"] = hourly_us_aqi_ozone
        hourly_data["us_aqi_sulphur_dioxide"] = hourly_us_aqi_sulphur_dioxide

        hourly_dataframe = pd.DataFrame(data = hourly_data)
        
        return hourly_dataframe

    # Get city dict
    city_info = get_city_info()
    
    # city_list
    city_list = list(city_info.keys())
    
    for city in city_list:
        city_file = f"./data/{city}_Air_Quality.csv"
        latitude = city_info[city]["lat"]
        longitude = city_info[city]["lon"]
        timezone = get_time_zone(city)
        start_date = "2022-07-29"
        end_date = pd.to_datetime("now") - pd.Timedelta(days = 1)
        end_date = end_date.strftime("%Y-%m-%d")
        df = get_historical_data(latitude, longitude, start_date, end_date, timezone)
        df.to_csv(city_file, index = False)
        time.sleep(60)
        
def update_Solar_Soil_data():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    def get_historical_data(lat, long, start, end, tz):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": long,
            "start_date": start,
            "end_date": end,
            "hourly": ["soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm", "soil_temperature_28_to_100cm", "soil_temperature_100_to_255cm", "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm", "soil_moisture_28_to_100cm", "soil_moisture_100_to_255cm", "shortwave_radiation", "direct_radiation", "diffuse_radiation", "direct_normal_irradiance", "global_tilted_irradiance", "terrestrial_radiation", "shortwave_radiation_instant", "direct_radiation_instant", "diffuse_radiation_instant", "direct_normal_irradiance_instant", "global_tilted_irradiance_instant", "terrestrial_radiation_instant"],
            "timezone": tz
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_soil_temperature_0_to_7cm = hourly.Variables(0).ValuesAsNumpy()
        hourly_soil_temperature_7_to_28cm = hourly.Variables(1).ValuesAsNumpy()
        hourly_soil_temperature_28_to_100cm = hourly.Variables(2).ValuesAsNumpy()
        hourly_soil_temperature_100_to_255cm = hourly.Variables(3).ValuesAsNumpy()
        hourly_soil_moisture_0_to_7cm = hourly.Variables(4).ValuesAsNumpy()
        hourly_soil_moisture_7_to_28cm = hourly.Variables(5).ValuesAsNumpy()
        hourly_soil_moisture_28_to_100cm = hourly.Variables(6).ValuesAsNumpy()
        hourly_soil_moisture_100_to_255cm = hourly.Variables(7).ValuesAsNumpy()
        hourly_shortwave_radiation = hourly.Variables(8).ValuesAsNumpy()
        hourly_direct_radiation = hourly.Variables(9).ValuesAsNumpy()
        hourly_diffuse_radiation = hourly.Variables(10).ValuesAsNumpy()
        hourly_direct_normal_irradiance = hourly.Variables(11).ValuesAsNumpy()
        hourly_global_tilted_irradiance = hourly.Variables(12).ValuesAsNumpy()
        hourly_terrestrial_radiation = hourly.Variables(13).ValuesAsNumpy()
        hourly_shortwave_radiation_instant = hourly.Variables(14).ValuesAsNumpy()
        hourly_direct_radiation_instant = hourly.Variables(15).ValuesAsNumpy()
        hourly_diffuse_radiation_instant = hourly.Variables(16).ValuesAsNumpy()
        hourly_direct_normal_irradiance_instant = hourly.Variables(17).ValuesAsNumpy()
        hourly_global_tilted_irradiance_instant = hourly.Variables(18).ValuesAsNumpy()
        hourly_terrestrial_radiation_instant = hourly.Variables(19).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["soil_temperature_0_to_7cm"] = hourly_soil_temperature_0_to_7cm
        hourly_data["soil_temperature_7_to_28cm"] = hourly_soil_temperature_7_to_28cm
        hourly_data["soil_temperature_28_to_100cm"] = hourly_soil_temperature_28_to_100cm
        hourly_data["soil_temperature_100_to_255cm"] = hourly_soil_temperature_100_to_255cm
        hourly_data["soil_moisture_0_to_7cm"] = hourly_soil_moisture_0_to_7cm
        hourly_data["soil_moisture_7_to_28cm"] = hourly_soil_moisture_7_to_28cm
        hourly_data["soil_moisture_28_to_100cm"] = hourly_soil_moisture_28_to_100cm
        hourly_data["soil_moisture_100_to_255cm"] = hourly_soil_moisture_100_to_255cm
        hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
        hourly_data["direct_radiation"] = hourly_direct_radiation
        hourly_data["diffuse_radiation"] = hourly_diffuse_radiation
        hourly_data["direct_normal_irradiance"] = hourly_direct_normal_irradiance
        hourly_data["global_tilted_irradiance"] = hourly_global_tilted_irradiance
        hourly_data["terrestrial_radiation"] = hourly_terrestrial_radiation
        hourly_data["shortwave_radiation_instant"] = hourly_shortwave_radiation_instant
        hourly_data["direct_radiation_instant"] = hourly_direct_radiation_instant
        hourly_data["diffuse_radiation_instant"] = hourly_diffuse_radiation_instant
        hourly_data["direct_normal_irradiance_instant"] = hourly_direct_normal_irradiance_instant
        hourly_data["global_tilted_irradiance_instant"] = hourly_global_tilted_irradiance_instant
        hourly_data["terrestrial_radiation_instant"] = hourly_terrestrial_radiation_instant

        hourly_dataframe = pd.DataFrame(data = hourly_data)
        return hourly_dataframe

    def get_forecast(latitude, longitude, past):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["soil_temperature_0cm", "soil_temperature_6cm", "soil_temperature_18cm", "soil_temperature_54cm", "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", "soil_moisture_27_to_81cm", "shortwave_radiation", "direct_radiation", "diffuse_radiation", "direct_normal_irradiance", "global_tilted_irradiance", "terrestrial_radiation", "shortwave_radiation_instant", "direct_radiation_instant", "diffuse_radiation_instant", "direct_normal_irradiance_instant", "global_tilted_irradiance_instant", "terrestrial_radiation_instant"],
            "past_days": past
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_soil_temperature_0cm = hourly.Variables(0).ValuesAsNumpy()
        hourly_soil_temperature_6cm = hourly.Variables(1).ValuesAsNumpy()
        hourly_soil_temperature_18cm = hourly.Variables(2).ValuesAsNumpy()
        hourly_soil_temperature_54cm = hourly.Variables(3).ValuesAsNumpy()
        hourly_soil_moisture_0_to_1cm = hourly.Variables(4).ValuesAsNumpy()
        hourly_soil_moisture_1_to_3cm = hourly.Variables(5).ValuesAsNumpy()
        hourly_soil_moisture_3_to_9cm = hourly.Variables(6).ValuesAsNumpy()
        hourly_soil_moisture_9_to_27cm = hourly.Variables(7).ValuesAsNumpy()
        hourly_soil_moisture_27_to_81cm = hourly.Variables(8).ValuesAsNumpy()
        hourly_shortwave_radiation = hourly.Variables(9).ValuesAsNumpy()
        hourly_direct_radiation = hourly.Variables(10).ValuesAsNumpy()
        hourly_diffuse_radiation = hourly.Variables(11).ValuesAsNumpy()
        hourly_direct_normal_irradiance = hourly.Variables(12).ValuesAsNumpy()
        hourly_global_tilted_irradiance = hourly.Variables(13).ValuesAsNumpy()
        hourly_terrestrial_radiation = hourly.Variables(14).ValuesAsNumpy()
        hourly_shortwave_radiation_instant = hourly.Variables(15).ValuesAsNumpy()
        hourly_direct_radiation_instant = hourly.Variables(16).ValuesAsNumpy()
        hourly_diffuse_radiation_instant = hourly.Variables(17).ValuesAsNumpy()
        hourly_direct_normal_irradiance_instant = hourly.Variables(18).ValuesAsNumpy()
        hourly_global_tilted_irradiance_instant = hourly.Variables(19).ValuesAsNumpy()
        hourly_terrestrial_radiation_instant = hourly.Variables(20).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm
        hourly_data["soil_temperature_6cm"] = hourly_soil_temperature_6cm
        hourly_data["soil_temperature_18cm"] = hourly_soil_temperature_18cm
        hourly_data["soil_temperature_54cm"] = hourly_soil_temperature_54cm
        hourly_data["soil_moisture_0_to_1cm"] = hourly_soil_moisture_0_to_1cm
        hourly_data["soil_moisture_1_to_3cm"] = hourly_soil_moisture_1_to_3cm
        hourly_data["soil_moisture_3_to_9cm"] = hourly_soil_moisture_3_to_9cm
        hourly_data["soil_moisture_9_to_27cm"] = hourly_soil_moisture_9_to_27cm
        hourly_data["soil_moisture_27_to_81cm"] = hourly_soil_moisture_27_to_81cm
        hourly_data["shortwave_radiation"] = hourly_shortwave_radiation
        hourly_data["direct_radiation"] = hourly_direct_radiation
        hourly_data["diffuse_radiation"] = hourly_diffuse_radiation
        hourly_data["direct_normal_irradiance"] = hourly_direct_normal_irradiance
        hourly_data["global_tilted_irradiance"] = hourly_global_tilted_irradiance
        hourly_data["terrestrial_radiation"] = hourly_terrestrial_radiation
        hourly_data["shortwave_radiation_instant"] = hourly_shortwave_radiation_instant
        hourly_data["direct_radiation_instant"] = hourly_direct_radiation_instant
        hourly_data["diffuse_radiation_instant"] = hourly_diffuse_radiation_instant
        hourly_data["direct_normal_irradiance_instant"] = hourly_direct_normal_irradiance_instant
        hourly_data["global_tilted_irradiance_instant"] = hourly_global_tilted_irradiance_instant
        hourly_data["terrestrial_radiation_instant"] = hourly_terrestrial_radiation_instant

        hourly_dataframe = pd.DataFrame(data = hourly_data)
        return hourly_dataframe

    # Get city dict
    city_info = get_city_info()
    
    # city_list
    city_list = list(city_info.keys())
    
    for city in city_list:
        city_file = f"./data/{city}_Solar_Soil.csv"
        latitude = city_info[city]["lat"]
        longitude = city_info[city]["lon"]
        timezone = get_time_zone(city)
        old_df = pd.read_csv(city_file)
        old_df["date"] = pd.to_datetime(old_df["date"])
        
        start = old_df["date"].max().date()
        
        end = pd.to_datetime("now").date()
        
        day_diff = (end - start).days
        
        new_df = get_historical_data(latitude, longitude, start, end, timezone)
        new_df['date'] = pd.to_datetime(new_df['date'])
        new_df["date"] = new_df["date"].dt.tz_convert(timezone)
        
        last_date = old_df['date'].iloc[-1]
        new_df = new_df[new_df['date'] > last_date]
        new_df = new_df[new_df['date'].dt.date < end]
        new_df = pd.concat([old_df, new_df], ignore_index=True)
        new_df.to_csv(city_file, index=False)
        time.sleep(60)

def update_Air_Quality_data():
    cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    def get_historical_data(lat, long, start, end, tz):
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": lat,
            "longitude": long,
            "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "aerosol_optical_depth", "dust", "uv_index", "uv_index_clear_sky", "ammonia", "alder_pollen", "birch_pollen", "grass_pollen", "mugwort_pollen", "olive_pollen", "ragweed_pollen", "us_aqi", "us_aqi_pm2_5", "us_aqi_pm10", "us_aqi_nitrogen_dioxide", "us_aqi_carbon_monoxide", "us_aqi_ozone", "us_aqi_sulphur_dioxide"],
            "timezone": tz,
            "start_date": start,
            "end_date": end
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        hourly = response.Hourly()
        hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
        hourly_pm2_5 = hourly.Variables(1).ValuesAsNumpy()
        hourly_carbon_monoxide = hourly.Variables(2).ValuesAsNumpy()
        hourly_nitrogen_dioxide = hourly.Variables(3).ValuesAsNumpy()
        hourly_sulphur_dioxide = hourly.Variables(4).ValuesAsNumpy()
        hourly_ozone = hourly.Variables(5).ValuesAsNumpy()
        hourly_aerosol_optical_depth = hourly.Variables(6).ValuesAsNumpy()
        hourly_dust = hourly.Variables(7).ValuesAsNumpy()
        hourly_uv_index = hourly.Variables(8).ValuesAsNumpy()
        hourly_uv_index_clear_sky = hourly.Variables(9).ValuesAsNumpy()
        hourly_ammonia = hourly.Variables(10).ValuesAsNumpy()
        hourly_alder_pollen = hourly.Variables(11).ValuesAsNumpy()
        hourly_birch_pollen = hourly.Variables(12).ValuesAsNumpy()
        hourly_grass_pollen = hourly.Variables(13).ValuesAsNumpy()
        hourly_mugwort_pollen = hourly.Variables(14).ValuesAsNumpy()
        hourly_olive_pollen = hourly.Variables(15).ValuesAsNumpy()
        hourly_ragweed_pollen = hourly.Variables(16).ValuesAsNumpy()
        hourly_us_aqi = hourly.Variables(17).ValuesAsNumpy()
        hourly_us_aqi_pm2_5 = hourly.Variables(18).ValuesAsNumpy()
        hourly_us_aqi_pm10 = hourly.Variables(19).ValuesAsNumpy()
        hourly_us_aqi_nitrogen_dioxide = hourly.Variables(20).ValuesAsNumpy()
        hourly_us_aqi_carbon_monoxide = hourly.Variables(21).ValuesAsNumpy()
        hourly_us_aqi_ozone = hourly.Variables(22).ValuesAsNumpy()
        hourly_us_aqi_sulphur_dioxide = hourly.Variables(23).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["pm10"] = hourly_pm10
        hourly_data["pm2_5"] = hourly_pm2_5
        hourly_data["carbon_monoxide"] = hourly_carbon_monoxide
        hourly_data["nitrogen_dioxide"] = hourly_nitrogen_dioxide
        hourly_data["sulphur_dioxide"] = hourly_sulphur_dioxide
        hourly_data["ozone"] = hourly_ozone
        hourly_data["aerosol_optical_depth"] = hourly_aerosol_optical_depth
        hourly_data["dust"] = hourly_dust
        hourly_data["uv_index"] = hourly_uv_index
        hourly_data["uv_index_clear_sky"] = hourly_uv_index_clear_sky
        hourly_data["ammonia"] = hourly_ammonia
        hourly_data["alder_pollen"] = hourly_alder_pollen
        hourly_data["birch_pollen"] = hourly_birch_pollen
        hourly_data["grass_pollen"] = hourly_grass_pollen
        hourly_data["mugwort_pollen"] = hourly_mugwort_pollen
        hourly_data["olive_pollen"] = hourly_olive_pollen
        hourly_data["ragweed_pollen"] = hourly_ragweed_pollen
        hourly_data["us_aqi"] = hourly_us_aqi
        hourly_data["us_aqi_pm2_5"] = hourly_us_aqi_pm2_5
        hourly_data["us_aqi_pm10"] = hourly_us_aqi_pm10
        hourly_data["us_aqi_nitrogen_dioxide"] = hourly_us_aqi_nitrogen_dioxide
        hourly_data["us_aqi_carbon_monoxide"] = hourly_us_aqi_carbon_monoxide
        hourly_data["us_aqi_ozone"] = hourly_us_aqi_ozone
        hourly_data["us_aqi_sulphur_dioxide"] = hourly_us_aqi_sulphur_dioxide

        hourly_dataframe = pd.DataFrame(data = hourly_data)
        return hourly_dataframe

    # Get city dict
    city_info = get_city_info()
    
    # city_list
    city_list = list(city_info.keys())
    
    for city in city_list:
        city_file = f"./data/{city}_Air_Quality.csv"
        latitude = city_info[city]["lat"]
        longitude = city_info[city]["lon"]
        timezone = get_time_zone(city)
        old_df = pd.read_csv(city_file)
        old_df["date"] = pd.to_datetime(old_df["date"])
        
        start = old_df["date"].max().date()
        
        end = pd.to_datetime("now").date()
        
        day_diff = (end - start).days
        
        new_df = get_historical_data(latitude, longitude, start, end, timezone)
        new_df['date'] = pd.to_datetime(new_df['date'])
        new_df["date"] = new_df["date"].dt.tz_convert(timezone)
        
        last_date = old_df['date'].iloc[-1]
        new_df = new_df[new_df['date'] > last_date]
        new_df = new_df[new_df['date'].dt.date < end]
        new_df = pd.concat([old_df, new_df], ignore_index=True)
        new_df.to_csv(city_file, index=False)
        time.sleep(60)