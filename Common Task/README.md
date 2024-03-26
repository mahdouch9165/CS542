# CS 542 Common Task

## Mahdi Khemakhem
## BUID: U18251472
## Email: mahdouch@bu.edu

## Guide

The following folder contains all of the code/data/notes/images relating to the common task. 

## Data collection:

Data was kept inside this folder at organize/data. The data can be updated daily by running the second cell in the run.ipynb notebook under organized. Data is collected from the following sources:

### 1. NOAA Daily Aggregated Daily Weather Data 
url: https://scacis.rcc-acis.org/

### 2. Open-Meteo Daily Historical Climate Data
url: https://archive-api.open-meteo.com/v1/archive

### 3. NOAA WRH 5-Minute Site Data
url: https://www.weather.gov/wrh/timeseries?site={insert_site symbol}

### 4. Open-Meteo Hourly Historical Solar Radiation, and Soil Data
url: https://archive-api.open-meteo.com/v1/archive

### 5. Open-Meteo Hourly Historical Air Quality Data
url: https://archive-api.open-meteo.com/v1/archive

## Training:

Training code can be found under organized:

- LSTM_notebook
- Ensemble_Regression_notebook
  
## API-Trading:

API trading can be automatically run by running the thrid cell of the run.ipynb notebook under organized. The code is located under organized/trading. Trade logs can be found under organized/history.

## Report:

The report can be found under report.ipynb, which contains my notes and thoughts as I build this project.

## Helpers:

The bulk of the code is under util files (kalshi/df/regular). These functions support the training and trading notebooks, and allow for a more polished codebase.

## Trading Logs and Account Balance:

Logs can be found under KalshiLogs.csv, and images folder. Account balance can be found under organized/images.

## Consideration:

I removed my credentials, from Kalshi utils, and my API keys from the code. Please replace them with your own, if you want to run the code.