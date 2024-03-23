from utils import *

# run update_noaa_data() with retries
num_retries = 10
for i in range(num_retries):
    try:
        update_NOAA_data()
        break
    except Exception as e:
        print(f"Error: {e}")
        print(f"Retrying... {i+1}/{num_retries}")
        time.sleep(10)