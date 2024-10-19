import re

import pandas as pd
from geopy.distance import geodesic
from tqdm import tqdm

# Load the data
blue_data = pd.read_csv(
    "data/blueribbon.csv"
)  # Contains NAME, LATITUDE, LONGITUDE, ADDRESS
mct_data = pd.read_csv(
    "data/JEJU_PROCESSED.csv", encoding="cp949"
)  # Contains MCT_NM, LATITUDE, LONGITUDE


def clean_place_name(place_name):
    # Remove content inside parentheses (including the parentheses)
    if isinstance(place_name, str):  # Check if the value is a string
        place_name = re.sub(r"\(.*?\)", "", place_name)

        # Remove whitespace, commas, and periods
        place_name = re.sub(r"[,\.\s]+", "", place_name)

    return place_name


# Function to calculate distance in meters between two points
def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters


# Keep only the last occurrence of each MCT_NM
mct_data = mct_data.drop_duplicates(subset=["MCT_NM"], keep="last")

# Add cleaned names to the data for matching
blue_data["CLEANED_NAME"] = blue_data["NAME"].apply(clean_place_name)
mct_data["CLEANED_MCT_NM"] = mct_data["MCT_NM"].apply(clean_place_name)

# Create a list to store the matched results
matches = []

# Iterate through each row in the BLUE data
for blue_idx, blue_row in tqdm(blue_data.iterrows(), total=len(blue_data)):
    blue_name = blue_row["CLEANED_NAME"]
    blue_lat = blue_row["LATITUDE"]
    blue_lon = blue_row["LONGITUDE"]

    # Step 1: Check for exact match in MCT_DATA (using cleaned names)
    exact_matches = mct_data[mct_data["CLEANED_MCT_NM"] == blue_name]

    if len(exact_matches) == 1:
        # print(exact_matches.iloc[0]['MCT_NM'], blue_row['NAME'])
        # If there's exactly one match, record it with the original names
        matches.append(
            {"MCT_NAME": exact_matches.iloc[0]["MCT_NM"], "BLUE_NAME": blue_row["NAME"]}
        )
    else:
        # Step 2: Find partial matches (using cleaned names)
        partial_matches = mct_data[
            mct_data["CLEANED_MCT_NM"].str.contains(blue_name, na=False)
        ]

        if not partial_matches.empty:
            # Step 3: Calculate distances for partial matches
            valid_matches = []
            for idx, mct_row in partial_matches.iterrows():
                mct_name = mct_row["MCT_NM"]
                mct_lat = mct_row["LATITUDE"]
                mct_lon = mct_row["LONGITUDE"]

                # Calculate distance
                distance = calculate_distance(blue_lat, blue_lon, mct_lat, mct_lon)

                if distance <= 100:
                    valid_matches.append(
                        {
                            "MCT_NAME": mct_name,
                            "BLUE_NAME": blue_row["NAME"],
                            "distance": distance,
                        }
                    )

            # Step 4: If only one valid match within 100m, add it; otherwise, discard
            if len(valid_matches) == 1:
                matches.append(
                    {
                        "MCT_NAME": valid_matches[0]["MCT_NAME"],
                        "BLUE_NAME": blue_row["NAME"],
                    }
                )

# Create a DataFrame for the matched results
matched_df = pd.DataFrame(matches)

# Save the result to a CSV file
matched_df.to_csv("MCT_BLUE_MATCHED.csv", index=False, encoding="utf-8-sig")

print("Matching complete. Results saved to 'MCT_BLUE_MATCHED.csv'")

# Create a DataFrame for the matched results
matched_df = pd.DataFrame(matches)
print(len(matched_df))

# Save the result to a CSV file
matched_df.to_csv("data/MCT_BLUE_MATCHED.csv", index=False, encoding="cp949")

print("Matching complete. Results saved to 'MCT_BLUE_MATCHED.csv'")
