
# Function to calculate distance between two lat/lon points using the Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    from geopy.distance import distance
    return distance((lat1, lon1), (lat2, lon2)).m