import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Assuming df already has the distance columns: 'Dist_Nominatim_Kakao', 'Dist_Google_Kakao', 'Dist_Nominatim_Google'
df = pd.read_csv("data/sample_geolocation_comparison_updated.csv", encoding="cp949")

# Replace NaN values with a small number to avoid issues with log scale
df["Dist_Nominatim_Kakao"] = df["Dist_Nominatim_Kakao"].fillna(1)
df["Dist_Google_Kakao"] = df["Dist_Google_Kakao"].fillna(1)
df["Dist_Nominatim_Google"] = df["Distance"].fillna(1)

# Create a figure for the plot
plt.figure(figsize=(10, 6))

# Plot histogram for each distance on a log scale
plt.hist(
    np.log10(df["Dist_Nominatim_Kakao"]),
    bins=50,
    alpha=0.5,
    label="Nominatim-Kakao",
    edgecolor="k",
)
plt.hist(
    np.log10(df["Dist_Google_Kakao"]),
    bins=50,
    alpha=0.5,
    label="Google-Kakao",
    edgecolor="k",
)
plt.hist(
    np.log10(df["Dist_Nominatim_Google"]),
    bins=50,
    alpha=0.5,
    label="Nominatim-Google",
    edgecolor="k",
)

# Set plot title and labels
plt.title("Distribution of Log10 Distances Between Nominatim, Google, and Kakao")
plt.xlabel("Distance (meters, log scale)")
plt.ylabel("Frequency")

# Modify the x-axis ticks to show original distance values instead of log scale values
ticks = [10, 100, 1000, 10000, 100000]  # Example tick values in meters
tick_labels = [str(tick) for tick in ticks]
plt.xticks(np.log10(ticks), tick_labels)

# Show grid and legend
plt.grid(True)
plt.legend()

# Show the plot
plt.show()
