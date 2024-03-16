import json
import os

# Helper function to load the city coordinates
# Ensures that code like this does not get repeated in multiple scripts
def load_city_coords():
    path = os.path.join(os.path.dirname(__file__), "city_coords.json")
    with open(path, "r") as f:
        data = json.load(f)
    
    # Extract city variables
    miami_coords = data[0]
    nyc_coords = data[1]
    chicago_coords = data[2]
    austin_coords = data[3]

    # Return them to the requesting script
    return miami_coords, nyc_coords, chicago_coords, austin_coords
