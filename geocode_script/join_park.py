import pandas as pd
from geopy.distance import geodesic
from tqdm import tqdm

# Load the data
mct_data = pd.read_csv(
    "data/JEJU_PROCESSED.csv", encoding="cp949"
)  # Contains MCT_NM, OP_YMD, LATITUDE, LONGITUDE
parking_data = pd.read_csv(
    "data/JEJU_PARKING.csv", encoding="cp949"
)  # Contains PARKING_NAME, ADDR, LATITUDE, LONGITUDE

# Remove duplicates from MCT_DATA based on MCT_NM and OP_YMD
mct_data = mct_data.drop_duplicates(subset=["MCT_NM", "OP_YMD"])


# Function to calculate the distance between two coordinates in meters
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters


# Create a list to store the matched results
matches = []

# Iterate over MCT_DATA and find the closest parking lot for each store within 500m
for idx, mct_row in tqdm(mct_data.iterrows(), total=len(mct_data)):
    mct_name = mct_row["MCT_NM"]
    mct_lat = mct_row["LATITUDE"]
    mct_lon = mct_row["LONGITUDE"]

    # Restaurant location
    restaurant_location = (mct_lat, mct_lon)

    # Step 1: Filter parking lots that are within a rough range of 500m based on latitude/longitude differences
    lat_threshold = 500 / 111320  # 500 meters to degrees of latitude
    filtered_parking = parking_data[
        (abs(parking_data["Latitude"] - mct_lat) <= lat_threshold)
        & (abs(parking_data["Longitude"] - mct_lon) <= lat_threshold)
    ]

    # Step 2: Initialize variables to find the closest parking lot
    closest_parking = None
    closest_distance = float("inf")

    # Step 3: Check distances using geopy for precise calculation
    for _, parking_row in filtered_parking.iterrows():
        parking_lat = parking_row["Latitude"]
        parking_lon = parking_row["Longitude"]
        parking_name = parking_row["PARKING_NAME"]
        parking_address = parking_row["ADDR"]

        # Calculate the distance using geodesic
        distance = calculate_distance(mct_lat, mct_lon, parking_lat, parking_lon)

        # If the parking lot is within 500 meters and closer than the previous one, update the closest
        if distance <= 500 and distance < closest_distance:
            closest_parking = f"{parking_name}({parking_address})"
            closest_distance = distance

    # Step 4: If no parking is found within 500m, set 'NONE'
    if closest_parking is None:
        closest_parking = "NONE"

    # Step 5: Store the result
    matches.append(
        {
            "MCT_NM": mct_name,
            "OP_YMD": mct_row["OP_YMD"],
            "PARK_NAME_ADDR": closest_parking,
        }
    )

# Create a DataFrame for the matched results
matched_df = pd.DataFrame(matches)

# Save the result to a CSV file
matched_df.to_csv("data/MCT_PARKING_MATCHED.csv", index=False, encoding="cp949")

print("Matching complete. Results saved to 'MCT_PARKING_MATCHED.csv'")
