import numpy as np
import pandas as pd
from geopy.distance import geodesic

# Read the data
df1 = pd.read_csv("data/JEJU_PARKING.csv", encoding="cp949")
df2 = pd.read_csv("data/JEJU_PARKING (사본).csv", encoding="cp949")


# Function to calculate the geodesic distance between two points (in meters)
def calculate_distance(row):
    try:
        coords_1 = (row["Latitude_df1"], row["Longitude_df1"])
        coords_2 = (row["Latitude_df2"], row["Longitude_df2"])
        return geodesic(coords_1, coords_2).meters
    except Exception as e:
        print(f"Error calculating distance: {e}")
        return None


# Rename latitude and longitude columns for clarity
df1["Latitude_df1"] = df1["Latitude"]
df1["Longitude_df1"] = df1["Longitude"]
df2["Latitude_df2"] = df2["Latitude"]
df2["Longitude_df2"] = df2["Longitude"]

# Merge the two dataframes on the index
merged_df = pd.merge(df1, df2, left_index=True, right_index=True)

# Drop rows where either Latitude or Longitude is missing in df1 or df2
merged_df_cleaned = merged_df.dropna(
    subset=["Latitude_df1", "Longitude_df1", "Latitude_df2", "Longitude_df2"]
)

# Apply the distance calculation after dropping NaN rows
merged_df_cleaned["distance"] = merged_df_cleaned.apply(calculate_distance, axis=1)

# Display the result
# print(
#     merged_df_cleaned[
#         ["Latitude_df1", "Longitude_df1", "Latitude_df2", "Longitude_df2", "distance"]
#     ]
# )

# Sort the dataframe by distance in ascending order
sorted_df = merged_df_cleaned.sort_values(by="distance")

# Display the sorted result
print(
    sorted_df[
        ["Latitude_df1", "Longitude_df1", "Latitude_df2", "Longitude_df2", "distance"]
    ]
)

import matplotlib.pyplot as plt

# Plot the distances on a log scale but change the x-axis ticks to show original distances
plt.figure(figsize=(10, 6))
plt.hist(np.log10(sorted_df["distance"]), bins=50, edgecolor="k")
plt.title("Distribution of Log10 Distances")
plt.xlabel("Distance (meters)")
plt.ylabel("Frequency")
plt.grid(True)

# Modify the x-axis ticks to show the original distance values
ticks = [10, 100, 1000, 10000, 100000]  # Example ticks in meters
tick_labels = [str(tick) for tick in ticks]
plt.xticks(np.log10(ticks), tick_labels)

plt.show()
