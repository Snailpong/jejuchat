import time

import pandas as pd
import requests
from geopy.distance import geodesic
from tqdm import tqdm

from utils.api_key import kakao_rest_api_key


# Function to get latitude and longitude from Kakao's API
def get_lat_lon_kakao(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {kakao_rest_api_key}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["documents"]:
                lat = data["documents"][0]["y"]  # Latitude
                lon = data["documents"][0]["x"]  # Longitude
                return float(lat), float(lon)
            else:
                return None, None  # No results found
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None, None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None, None


# Function to calculate distance between two coordinates
def calculate_distance(coords_1, coords_2):
    if None in coords_1 or None in coords_2:
        return None
    return geodesic(coords_1, coords_2).meters


# Load the CSV containing Nominatim and Google Maps data
df = pd.read_csv("data/sample_geolocation_comparison.csv", encoding="cp949")

# Add new columns for Kakao Map geocoding and distances
df["Lat_Kakao"] = None
df["Lon_Kakao"] = None
df["Dist_Nominatim_Kakao"] = None
df["Dist_Google_Kakao"] = None

# Loop through each address, fetch lat/lon from Kakao API, and calculate distances
for idx, row in tqdm(
    df.iterrows(), total=len(df), desc="Processing Kakao geocoding and distances"
):
    address = row["Address"]

    # Get Kakao coordinates
    lat_kakao, lon_kakao = get_lat_lon_kakao(address)
    df.at[idx, "Lat_Kakao"] = lat_kakao
    df.at[idx, "Lon_Kakao"] = lon_kakao

    # Calculate distances if Kakao coordinates are available
    if lat_kakao and lon_kakao:
        # Distance between Nominatim and Kakao
        df.at[idx, "Dist_Nominatim_Kakao"] = calculate_distance(
            (row["Lat_Nominatim"], row["Lon_Nominatim"]), (lat_kakao, lon_kakao)
        )

        # Distance between Google Maps and Kakao
        df.at[idx, "Dist_Google_Kakao"] = calculate_distance(
            (row["Lat_Google"], row["Lon_Google"]), (lat_kakao, lon_kakao)
        )

# Save the updated results to CSV
df.to_csv(
    "data/sample_geolocation_comparison_updated.csv", index=False, encoding="cp949"
)

# Print the first few rows for verification
print(df.head())
