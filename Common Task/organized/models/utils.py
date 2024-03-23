import numpy as np
import pandas as pd

def load_NOAA_df(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_OM_df(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()
    df['date'] = df['date'].str.split(' ').str[0]
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_MS_df(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.lower()
    # rename time to date
    df = df.rename(columns={'time':'date'})
    df['date'] = pd.to_datetime(df['date'])
    return df

def merge(noaa_df, om_df):
    df = noaa_df.copy()
    
    # Cycle features
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['day_of_year'] = df['date'].dt.dayofyear
    df['sin_day'] = np.sin(2 * np.pi * df['day_of_year']/365)
    df['cos_day'] = np.cos(2 * np.pi * df['day_of_year']/365)
    
    # drop atobstemp 
    df.drop(columns=['atobstemperature', 'snowdepth', 'snowfallnormal', 
                     'snowfalldeparture', 'avgtemperature', 'avgtemperaturedeparture', 
                     'hdd', 'hdddeparture', 'cdd', 'cdddeparture', 'gdd'], inplace=True)
    
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
    
        # Apply custom function
    df['maxtemperature'] = df.apply(fill_missing_from_dict, args=('maxtemperature', max_temp_om_dict), axis=1)
    df['mintemperature'] = df.apply(fill_missing_from_dict, args=('mintemperature', min_temp_om_dict), axis=1)
    df['snowfall'] = df.apply(fill_missing_from_dict, args=('snowfall', snowfall_om_dict), axis=1)
    
    
    # Recalcualte departure
    df['maxtemperaturedeparture'] = df['maxtemperature'] - df['maxtemperaturenormal']
    df['mintemperaturedeparture'] = df['mintemperature'] - df['mintemperaturenormal']
    
    # Reverse calculate precipitation from precipitation normal and departure
    df['precipitation'] = df['precipitationnormal'] + df['precipitationdeparture']
    
    df['precipitation'] = df.apply(fill_missing_from_dict, args=('precipitation', precipitation_om_dict), axis=1)
    df['precipitationdeparture'] = df['precipitation'] - df['precipitationnormal']
    
    df['next_day_max_temp_normal'] = df['maxtemperaturenormal'].shift(-1)
    df['next_day_min_temp_normal'] = df['mintemperaturenormal'].shift(-1)
    df['next_day_avg_temp_normal'] = df['avgtemperaturenormal'].shift(-1)
    df['next_day_precipitation_normal'] = df['precipitationnormal'].shift(-1)
    df['next_day_CDD_normal'] = df['cddnormal'].shift(-1)
    df['next_day_HDD_normal'] = df['hddnormal'].shift(-1)
    
    df = df.merge(om_df, on='date', how='left')
    
    # Turn weather_code into one hot encoding
    df = pd.get_dummies(df, columns=['weather_code'])
        
    # Target 
    df['next_day_max_temp'] = df['maxtemperature'].shift(-1)
    
    last_row = df.iloc[-2]
    df = df[:-2]

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

def update_df_solo(old_df):
    df = old_df.copy()

    # cycle features
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['day_of_year'] = df['date'].dt.dayofyear
    df['sin_day'] = np.sin(2 * np.pi * df['day_of_year']/365)
    df['cos_day'] = np.cos(2 * np.pi * df['day_of_year']/365)
    
    # drop AtObsTemperature
    df = df.drop(columns=['atobstemperature', 'snowfallnormal', 'snowfalldeparture', 'snowdepth', 'avgtemperature', 'avgtemperaturedeparture', 'cdd', 'hdddeparture', 'cdddeparture', 'gdd', 'hdd'])
    
    df['precipitation'] = df['precipitationnormal'] + df['precipitationdeparture']
    
    # Carry future values.
    df['next_day_max_temp_normal'] = df['maxtemperaturenormal'].shift(-1)
    df['next_day_min_temp_normal'] = df['mintemperaturenormal'].shift(-1)
    df['next_day_avg_temp_normal'] = df['avgtemperaturenormal'].shift(-1)
    df['next_day_precipitation_normal'] = df['precipitationnormal'].shift(-1)
    df['next_day_CDD_normal'] = df['cddnormal'].shift(-1)
    df['next_day_HDD_normal'] = df['hddnormal'].shift(-1)
    
    # Target 
    df['next_day_max_temp'] = df['maxtemperature'].shift(-1)
    
    # drop the final row
    last_row = df.iloc[-2]
    df = df[:-2]
    
    df = df.dropna()
    
    return df, last_row

def update_df_solo_v2(old_df):
    df = old_df.copy()

    # cycle features
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['day_of_year'] = df['date'].dt.dayofyear
    df['sin_day'] = np.sin(2 * np.pi * df['day_of_year']/365)
    df['cos_day'] = np.cos(2 * np.pi * df['day_of_year']/365)
    
    # drop AtObsTemperature
    df = df.drop(columns=['atobstemperature', 'snowdepth'])
    
    df['precipitation'] = df['precipitationnormal'] + df['precipitationdeparture']
    df['snowfall'] = df['snowfallnormal'] + df['snowfalldeparture']
    
    # Carry future values.
    df['next_day_max_temp_normal'] = df['maxtemperaturenormal'].shift(-1)
    df['next_day_min_temp_normal'] = df['mintemperaturenormal'].shift(-1)
    df['next_day_avg_temp_normal'] = df['avgtemperaturenormal'].shift(-1)
    df['next_day_precipitation_normal'] = df['precipitationnormal'].shift(-1)
    df['next_day_CDD_normal'] = df['cddnormal'].shift(-1)
    df['next_day_HDD_normal'] = df['hddnormal'].shift(-1)
    
    # Target 
    df['next_day_max_temp'] = df['maxtemperature'].shift(-1)
    
    # drop the final row
    last_row = df.iloc[-2]
    df = df[:-2]
    
    df = df.dropna()
    
    return df, last_row