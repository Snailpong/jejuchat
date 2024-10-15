import os
import random
import re
import time

import googlemaps
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from tqdm import tqdm

# Initialize the Nominatim geolocator
geolocator = Nominatim(user_agent="South Korea")

# Initialize Google Maps API (replace with your API key)
from utils.api_key import google_map_api_key

gmaps = googlemaps.Client(key=google_map_api_key)


def preprocess_address(address):
    if "번지" in address:
        address = address.split("번지")[0].strip()
    # Remove full words ending in "읍" or "면" (e.g., "한림읍", "애월읍")
    address = re.sub(r"\S*읍|\S*면", "", address).strip()
    return address


# Function to get lat/lon from Nominatim
def get_lat_lon_nominatim(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception as e:
        print(f"Nominatim error for address {address}: {e}")
        return None, None


# Function to get lat/lon from Google Maps
def get_lat_lon_googlemaps(address):
    try:
        location = gmaps.geocode(address)[0].get("geometry")
        if location:
            return location["location"]["lat"], location["location"]["lng"]
        return None, None
    except Exception as e:
        print(f"Google Maps error for address {address}: {e}")
        return None, None


# Function to calculate distance between two coordinates
def calculate_distance(coords_1, coords_2):
    if None in coords_1 or None in coords_2:
        return None
    return geodesic(coords_1, coords_2).meters


# Load MCT_DATA
mct_data = pd.read_csv("data/JEJU_MCT_DATA.csv", encoding="cp949")

# Clean up addresses and remove empty ones
mct_data = mct_data[~mct_data["ADDR"].str.strip().eq("")]

# Check if the sample file already exists, load it if it does
sample_file = "data/sample_geolocation_comparison.csv"
if os.path.exists(sample_file):
    sampled_df = pd.read_csv(sample_file, encoding="cp949")
    sampled_df = sampled_df.dropna(
        subset=["Lat_Nominatim", "Lon_Nominatim"]
    )  # Ensure valid Nominatim data
    num_existing_samples = len(sampled_df)
    print(f"Loaded {num_existing_samples} existing samples.")
else:
    sampled_df = pd.DataFrame(
        columns=[
            "Address",
            "Lat_Nominatim",
            "Lon_Nominatim",
            "Lat_Google",
            "Lon_Google",
            "Distance",
        ]
    )
    num_existing_samples = 0

# Sample addresses randomly until we have 200 valid Nominatim results
target_samples = 200
needed_samples = target_samples - num_existing_samples

sampled_addresses = []
# Sample addresses randomly until we have 200 valid Nominatim results and Google Maps coordinates
while len(sampled_df) < target_samples:
    # Randomly sample an address
    address = mct_data.sample(1)["ADDR"].values[0]

    # Preprocess address if needed
    # address = address.strip()  # Adjust based on your actual data
    address = preprocess_address(address)

    # Get Nominatim coordinates
    lat_nominatim, lon_nominatim = get_lat_lon_nominatim(address)

    if lat_nominatim and lon_nominatim:
        # Get Google Maps coordinates
        lat_google, lon_google = get_lat_lon_googlemaps(address)

        # Only add to the DataFrame if both Nominatim and Google Maps coordinates are available
        if lat_google and lon_google:
            distance = calculate_distance(
                (lat_nominatim, lon_nominatim), (lat_google, lon_google)
            )
            # Create a DataFrame for the new row
            new_row = pd.DataFrame(
                [
                    {
                        "Address": address,
                        "Lat_Nominatim": lat_nominatim,
                        "Lon_Nominatim": lon_nominatim,
                        "Lat_Google": lat_google,
                        "Lon_Google": lon_google,
                        "Distance": distance,
                    }
                ]
            )

            # Concatenate the new row to the existing DataFrame
            sampled_df = pd.concat([sampled_df, new_row], ignore_index=True)

            # Save progress to CSV after every successful addition
            sampled_df.to_csv(sample_file, index=False, encoding="cp949")
            print(distance)

# Print the first few results for verification
print(sampled_df.head())

import matplotlib.pyplot as plt
import numpy as np

# Plot the distances on a log scale but change the x-axis ticks to show original distances
plt.figure(figsize=(10, 6))
plt.hist(np.log10(sampled_df["Distance"]), bins=50, edgecolor="k")
plt.title("Distribution of Log10 Distances")
plt.xlabel("Distance (meters)")
plt.ylabel("Frequency")
plt.grid(True)

# Modify the x-axis ticks to show the original distance values
ticks = [10, 100, 1000, 10000, 100000]  # Example ticks in meters
tick_labels = [str(tick) for tick in ticks]
plt.xticks(np.log10(ticks), tick_labels)

plt.show()
