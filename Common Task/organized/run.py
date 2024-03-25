from utils import *
from models.utils import *
import pandas as pd
import numpy as np

# I found that loading the data initially is not the most consistent, so I did not include it in the run.py file.
# I have util functions that can be used to load the bulk of the data, but I will not include them here.
# For downloading the bulk data initially, I would recommend using the load_Source_data() function in the utils.py file.
# And using it in a python notebook for a more controlled/manual initial download.

# Step 1: Update the data
# This will update the data from the sources and include entries up until yesterday's date.
# This will provide us with a data entry that can be used for prediction of the current day.
num_retries = 10
for i in range(num_retries):
    try:
        #update_NOAA_data()
        break
    except Exception as e:
        print(f"Error: {e}")
        print(f"Retrying... {i+1}/{num_retries}")
        time.sleep(10)
        
for i in range(num_retries):
    try:
        #update_OM_data()
        break
    except Exception as e:
        print(f"Error: {e}")
        print(f"Retrying... {i+1}/{num_retries}")
        time.sleep(10)
        
for i in range(num_retries):
    try:
        #update_WRH_data()
        break
    except Exception as e:
        print(f"Error: {e}")
        print(f"Retrying... {i+1}/{num_retries}")
        time.sleep(10)
        
for i in range(num_retries):
    try:
        #update_Solar_Soil_data()
        break
    except Exception as e:
        print(f"Error: {e}")
        print(f"Retrying... {i+1}/{num_retries}")
        time.sleep(10)
        
for i in range(num_retries):
    try:
        #update_Air_Quality_data()
        break
    except Exception as e:
        print(f"Error: {e}")
        print(f"Retrying... {i+1}/{num_retries}")
        time.sleep(10)
        
print("Data updated successfully!")

# Step 2: Get city info and iterate through the cities
# The workflow will be as follows:
# 1. Load the data for the city
# 2. Load the models for the city
# 3. Look at the new data entry
# 4. Predict the new data entry, and update model weights
# 5. Predict the next day's data entry
# 6. Place a bet on Kalshi
# 7. Save the model weights
city_info = get_city_info()

for city in city_info.keys():
    # Get paths for the city data
    noaa_path = city_info[city]['noaa']
    om_path = city_info[city]['om']
    wrh_path = city_info[city]['wrh']
    aq_path = city_info[city]['aq']
    solar_path = city_info[city]['solar']
    
    # Load the data for the city
    # all_df is the main dataframe that contains all the data combined. I included subsets of the dataframes as well,
    # in case I need them in the future. Predictor is simply the last row. I extracted it so that it does not get
    # deleted by dropna.   
    daily_df, daily_df_2, daily_df_3, all_df, predictor_final = load_all_dfs(noaa_path, om_path, solar_path, wrh_path, aq_path)
    
    # get all_df[-1], to run a mini weight update


#daily_df, daily_df_2, daily_df_3, all_df, predictor_final = load_all_dfs(noaa_austin_path, om_austin_path, solar_austin_path, wrh_austin_path, air_austin_path)
#daily_df, daily_df_2, daily_df_3, all_df, predictor_final = load_all_dfs(noaa_nyc_path, om_nyc_path, solar_nyc_path, wrh_nyc_path, air_nyc_path)
#daily_df, daily_df_2, daily_df_3, all_df, predictor_final = load_all_dfs(noaa_miami_path, om_miami_path, solar_miami_path, wrh_miami_path, air_miami_path)
#daily_df, daily_df_2, daily_df_3, all_df, predictor_final = load_all_dfs(noaa_chicago_path, om_chicago_path, solar_chicago_path, wrh_chicago_path, air_chicago_path)
