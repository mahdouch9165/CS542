import os

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
    print(os.getcwd())
    
update_noaa_data()