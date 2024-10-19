import re

import pandas as pd


# Function to clean PLACE_NAME
def clean_place_name(place_name):
    # Remove content inside parentheses (including the parentheses)
    if isinstance(place_name, str):  # Check if the value is a string
        place_name = re.sub(r"\(.*?\)", "", place_name)

        # Remove whitespace, commas, and periods
        place_name = re.sub(r"[,\.\s]+", "", place_name)

    return place_name


# Load restaurant data from JEJU_PROCESSED.csv, selecting relevant columns
restaurant_df = pd.read_csv(
    "data/JEJU_PROCESSED.csv",
    usecols=["MCT_NM", "LATITUDE", "LONGITUDE"],
    encoding="cp949",
)

# Keep only the last occurrence of each MCT_NM
restaurant_df = restaurant_df.drop_duplicates(subset=["MCT_NM"], keep="last")

# Rename columns to match the required output
restaurant_df = restaurant_df.rename(
    columns={"MCT_NM": "PLACE_NAME", "LATITUDE": "LATITUDE", "LONGITUDE": "LONGITUDE"}
)

# Load tourist destination data from JEJU_TOUR.csv
tourist_df = pd.read_csv(
    "data/JEJU_TOUR.csv", usecols=["TOUR_NM", "Latitude", "Longitude"], encoding="cp949"
)

# Rename columns to match the required output
tourist_df = tourist_df.rename(
    columns={"TOUR_NM": "PLACE_NAME", "Latitude": "LATITUDE", "Longitude": "LONGITUDE"}
)

# Combine the two datasets
merged_df = pd.concat([restaurant_df, tourist_df], ignore_index=True)

merged_df = merged_df.drop_duplicates(subset=["PLACE_NAME"], keep="last")

# Apply the function to the PLACE_NAME column
merged_df["PLACE_NAME"] = merged_df["PLACE_NAME"].apply(clean_place_name)


# Save the merged dataset to a CSV file
output_file = "data/JEJU_PLACES_MERGED.csv"
merged_df.to_csv(output_file, index=False, encoding="cp949", index_label=False)

print(f"Merged file saved to {output_file}")
