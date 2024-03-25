import numpy as np
import pandas as pd

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

def load_NOAA_df(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()
    df['date'] = pd.to_datetime(df['date'])
    df = df.drop(columns=['atobstemperature'])
    df['precipitation'] = df['precipitationnormal'] + df['precipitationdeparture']
    return df

def load_OM_df(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()
    df['date'] = df['date'].str.split(' ').str[0]
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_Solar_Soil_df(path):
   df = pd.read_csv(path)
   df.columns = df.columns.str.lower()
   df['date'] = pd.to_datetime(df['date'], utc=True)
   city_name = path.split('/')[-1].split('_')[0]
   timezone = get_time_zone(city_name)
   # relocalize to the correct timezone
   df['date'] = df['date'].dt.tz_convert(timezone)
   # rename date to date_time
   df = df.rename(columns={'date': 'date_time'})
   df['date'] = df['date_time'].dt.date
   df['time'] = df['date_time'].dt.time
   df['year'] = df['date_time'].dt.year
   df['month'] = df['date_time'].dt.month
   df['day'] = df['date_time'].dt.day
   df['hour'] = df['date_time'].dt.hour
   df['minute'] = df['date_time'].dt.minute
   df['second'] = df['date_time'].dt.second
   df['day_of_year'] = df['date_time'].dt.dayofyear
   # sin ad cos of the day of the year
   df['sin_day'] = np.sin(2 * np.pi * df['day_of_year']/365)
   df['cos_day'] = np.cos(2 * np.pi * df['day_of_year']/365)
   return df

def load_Air_Quality_df(path):
   df = pd.read_csv(path)
   df.columns = df.columns.str.lower()
   df['date'] = pd.to_datetime(df['date'], utc=True)
   city_name = path.split('/')[-1].split('_')[0]
   timezone = get_time_zone(city_name)
   df['date'] = df['date'].dt.tz_convert(timezone)
   df = df.rename(columns={'date': 'date_time'})
   df['date'] = df['date_time'].dt.date
   df['time'] = df['date_time'].dt.time
   df['year'] = df['date_time'].dt.year
   df['month'] = df['date_time'].dt.month
   df['day'] = df['date_time'].dt.day
   df['hour'] = df['date_time'].dt.hour
   df['minute'] = df['date_time'].dt.minute
   df['second'] = df['date_time'].dt.second
   df['day_of_year'] = df['date_time'].dt.dayofyear
   # sin ad cos of the day of the year
   df['sin_day'] = np.sin(2 * np.pi * df['day_of_year']/365)
   df['cos_day'] = np.cos(2 * np.pi * df['day_of_year']/365)
   return df

def load_WRH_df(path):
   df = pd.read_csv(path)
   df.columns = df.columns.str.lower()
   df = df.drop(columns=['cloud_layer_2_code_set_1', 'sea_level_pressure_set_1',
      'cloud_layer_3_code_set_1', 'air_temp_high_6_hour_set_1',
      'air_temp_low_6_hour_set_1', 'pressure_change_code_set_1',
      'precip_accum_one_hour_set_1', 'weather_cond_code_set_1',
      'precip_accum_six_hour_set_1', 'wind_gust_set_1',
      'peak_wind_speed_set_1', 'pressure_tendency_set_1',
      'precip_accum_24_hour_set_1', 'precip_accum_three_hour_set_1',
      'snow_depth_set_1', 'air_temp_high_24_hour_set_1',
      'air_temp_low_24_hour_set_1', 'ceiling_set_1',
      'peak_wind_direction_set_1', 'dew_point_temperature_set_1',
      'metar_origin_set_1', 'weather_condition_set_1d',
      'cloud_layer_2_set_1d', 'cloud_layer_3_set_1d', 'wind_chill_set_1d',
      'heat_index_set_1d', 'metar_set_1', 'cloud_layer_1_set_1d', 'weather_summary_set_1d'])
   df['date_time'] = pd.to_datetime(df['date_time'], utc=True)
   # relocalize to the correct timezone
   city_name = path.split('/')[-1].split('_')[0]
   timezone = get_time_zone(city_name)
   # relocalize to the correct timezone
   df['date_time'] = df['date_time'].dt.tz_convert(timezone)
   df['date'] = df['date_time'].dt.date
   df['time'] = df['date_time'].dt.time
   df['year'] = df['date_time'].dt.year
   df['month'] = df['date_time'].dt.month
   df['day'] = df['date_time'].dt.day
   df['hour'] = df['date_time'].dt.hour
   df['minute'] = df['date_time'].dt.minute
   df['second'] = df['date_time'].dt.second
   df['day_of_year'] = df['date_time'].dt.dayofyear
   # sin ad cos of the day of the year
   df['sin_day'] = np.sin(2 * np.pi * df['day_of_year']/365)
   df['cos_day'] = np.cos(2 * np.pi * df['day_of_year']/365)
   columns_to_one_hot = ['wind_cardinal_direction_set_1d']
   df = pd.get_dummies(df, columns=columns_to_one_hot, dtype=int)
   df = df.dropna()
   return df

def merge_daily(noaa_df, om_df):
    df = noaa_df.copy()
    
    # Cycle features
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['day_of_year'] = df['date'].dt.dayofyear
    df['sin_day'] = np.sin(2 * np.pi * df['day_of_year']/365)
    df['cos_day'] = np.cos(2 * np.pi * df['day_of_year']/365)
    
    # drop atobstemp 
    df.drop(columns=['snowdepth', 'hdd', 'hdddeparture', 'cdd', 'cdddeparture', 'gdd', 'snowfallnormal', 'snowfalldeparture'], inplace=True)
    
    # Fill missing values
    max_temp_om_dict = om_df.set_index('date')['temperature_2m_max'].to_dict()
    min_temp_om_dict = om_df.set_index('date')['temperature_2m_min'].to_dict()
    snowfall_om_dict = om_df.set_index('date')['snowfall_sum'].to_dict()
    precipitation_om_dict = om_df.set_index('date')['precipitation_sum'].to_dict()
    
    def fill_missing_from_dict(row, column_name, reference_dict):
        if pd.isna(row[column_name]):
            return reference_dict.get(row['date'], np.nan)
        return row[column_name]

    # Apply custom function
    df['maxtemperature'] = df.apply(fill_missing_from_dict, args=('maxtemperature', max_temp_om_dict), axis=1)
    df['mintemperature'] = df.apply(fill_missing_from_dict, args=('mintemperature', min_temp_om_dict), axis=1)
    df['snowfall'] = df.apply(fill_missing_from_dict, args=('snowfall', snowfall_om_dict), axis=1)
    # For avgtemperature just draw from avgtemperaturenormal at the Nan values
    df['avgtemperature'] = df['avgtemperature'].fillna(df['avgtemperaturenormal'])    
    
    # Recalcualte departure
    df['maxtemperaturedeparture'] = df['maxtemperature'] - df['maxtemperaturenormal']
    df['mintemperaturedeparture'] = df['mintemperature'] - df['mintemperaturenormal']
    df['avgtemperaturedeparture'] = df['avgtemperature'] - df['avgtemperaturenormal']
    
    # Reverse calculate precipitation from precipitation normal and departure
    df['precipitation'] = df.apply(fill_missing_from_dict, args=('precipitation', precipitation_om_dict), axis=1)
    df['precipitationdeparture'] = df['precipitation'] - df['precipitationnormal']
    
    # look at the next day historical normals
    df['next_day_max_temp_normal'] = df['maxtemperaturenormal'].shift(-1)
    df['next_day_min_temp_normal'] = df['mintemperaturenormal'].shift(-1)
    df['next_day_avg_temp_normal'] = df['avgtemperaturenormal'].shift(-1)
    df['next_day_precipitation_normal'] = df['precipitationnormal'].shift(-1)
    df['next_day_CDD_normal'] = df['cddnormal'].shift(-1)
    df['next_day_HDD_normal'] = df['hddnormal'].shift(-1)
    
    df = df.merge(om_df, on='date', how='left')
    
    # Turn weather_code into one hot encoding
    df = pd.get_dummies(df, columns=['weather_code'], dtype=int)
        
    # Target 
    df['next_day_max_temp'] = df['maxtemperature'].shift(-1)
    
    last_row = df.iloc[-1]
    df = df[:-1]

    df = df.dropna()
    
    # readd last row dont use append
    last_row_df = pd.DataFrame(last_row).transpose()
    df = pd.concat([df, last_row_df], ignore_index=True)
    
    # add moving averages
    window_sizes = [3, 7, 14, 30]  # Specify the window sizes for moving averages
    
    for window in window_sizes:
        df[f'max_temp_ma_{window}'] = df['maxtemperature'].rolling(window=window).mean()
        df[f'min_temp_ma_{window}'] = df['mintemperature'].rolling(window=window).mean()
        df[f'avg_temp_ma_{window}'] = df['avgtemperaturenormal'].rolling(window=window).mean()
        df[f'precipitation_ma_{window}'] = df['precipitation'].rolling(window=window).mean()
    
    last_row = df.iloc[-1]
    
    df = df.dropna()    
    return df, last_row

def merge_hourly(wrh_df, ss_df):
    # filer wrh data to only keep minute 0 entries
    wrh_df = wrh_df[wrh_df['minute'] == 0]
    
    duplicate_columns = ['date', 'time', 'year', 'month', 'day', 'hour', 'minute', 'second', 'day_of_year', 'sin_day', 'cos_day']
    # aq_df = aq_df.drop(columns=duplicate_columns)
    ss_df = ss_df.drop(columns=duplicate_columns)

    # clean aq
    # aq_columns = ['ammonia', 'alder_pollen', 'birch_pollen', 'grass_pollen', 'mugwort_pollen', 'olive_pollen', 'ragweed_pollen']
    # aq_df = aq_df.drop(columns=aq_columns)

    # clean ss, only keep these columns
    ss_columns = ['date_time', 'terrestrial_radiation', 'terrestrial_radiation_instant']
    ss_df = ss_df[ss_columns]
    
    # merge wrh and aq data on date_time
    merged = pd.merge(wrh_df, ss_df, on='date_time', how='inner')
    # merged = pd.merge(merged, aq_df, on='date_time', how='inner')
    return merged

def merge_hourly_2(hourly_df, aq_df):
    duplicate_columns = ['date', 'time', 'year', 'month', 'day', 'hour', 'minute', 'second', 'day_of_year', 'sin_day', 'cos_day']
    aq_df = aq_df.drop(columns=duplicate_columns)
    
    # clean aq
    aq_columns = ['ammonia', 'alder_pollen', 'birch_pollen', 'grass_pollen', 'mugwort_pollen', 'olive_pollen', 'ragweed_pollen']
    aq_df = aq_df.drop(columns=aq_columns)
    
    merged = pd.merge(hourly_df, aq_df, on='date_time', how='inner')
    merged = merged.dropna()
    return merged

def add_target(noaa_df, merged):
    target = noaa_df[['date', 'maxtemperature']]
    target['date'] = pd.to_datetime(target['date'])
    target['next_day_maxtemperature'] = target['maxtemperature'].shift(-1)
    target = target.dropna()
    target = target.drop(columns='maxtemperature')
    merged['date'] = pd.to_datetime(merged['date'])
    merged = pd.merge(merged, target, on='date', how='inner')
    return merged

def turn_daily(df):
    columns_to_drop = ['time', 'date_time', 'hour', 'minute', 'second']
    df = df.drop(columns=columns_to_drop)
    df = df.groupby('date').mean().reset_index()
    return df

def simple_merge(daily, daily_2):
    duplicate_columns = ['year', 'month', 'day', 'day_of_year', 'sin_day', 'cos_day']
    daily['date'] = pd.to_datetime(daily['date'])
    daily_2['date'] = pd.to_datetime(daily_2['date'])
    daily_2 = daily_2.drop(columns=duplicate_columns)
    merged = pd.merge(daily, daily_2, on='date', how='inner')
    return merged

def all_merge(daily_1, daily_2, daily_3):
    duplicate_columns = ['year', 'month', 'day', 'day_of_year', 'sin_day', 'cos_day']
    daily_1['date'] = pd.to_datetime(daily_1['date'])
    daily_2['date'] = pd.to_datetime(daily_2['date'])
    daily_3['date'] = pd.to_datetime(daily_3['date'])
    daily_2 = daily_2.drop(columns=duplicate_columns)
    daily_3 = daily_3.drop(columns=duplicate_columns)
    # merge without dropping na
    merged = pd.merge(daily_1, daily_2, on='date', how='left')
    # common columns between merged and daily_3
    merged_columns = list(merged.columns)
    daily_3_columns = list(daily_3.columns)
    common_columns = list(set(merged_columns).intersection(daily_3_columns))
    # remove ['date'] from common columns
    common_columns.remove('date')
    daily_3 = daily_3.drop(columns=common_columns)
    merged = pd.merge(merged, daily_3, on='date', how='left')
    merged = merged.fillna(0)
    return merged

def load_all_dfs(noaa_path, om_path, ss_path, wrh_path, aq_path):
    noaa_df = load_NOAA_df(noaa_path)
    om_df = load_OM_df(om_path)
    wrh_df= load_WRH_df(wrh_path)
    aq_df = load_Air_Quality_df(aq_path)
    ss_df = load_Solar_Soil_df(ss_path)

    daily_df, predictor = merge_daily(noaa_df, om_df)
    hourly_df = merge_hourly(wrh_df, ss_df)
    hourly_df2 = merge_hourly_2(hourly_df, aq_df)
    daily_df_2 = turn_daily(hourly_df)
    daily_df_3 = turn_daily(hourly_df2)
    predictor_final = daily_df_3.drop(columns=['date','year', 'month', 'day', 'day_of_year', 'sin_day', 'cos_day']).iloc[-1]
    predictor_final = pd.concat([predictor, predictor_final], axis=0)
    all_df = all_merge(daily_df, daily_df_2, daily_df_3)
    daily_df_2 = simple_merge(daily_df, daily_df_2)
    daily_df_3 = simple_merge(daily_df, daily_df_3)
    return daily_df, daily_df_2, daily_df_3, all_df, predictor_final