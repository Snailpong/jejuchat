import os
import re
import requests
import pandas as pd
from tqdm import tqdm

from api_key import kakao_rest_api_key, google_map_api_key


def preprocess_address(address):
    if "번지" in address:
        address = address.split("번지")[0].strip()
    # Remove full words ending in "읍" or "면" (e.g., "한림읍", "애월읍")
    address = re.sub(r"\S*읍|\S*면", "", address).strip()
    return address


def add_address_kakao():
    # Kakao API endpoint and headers
    kakao_url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {kakao_rest_api_key}"}

    # Check if JEJU_ADDRESS.csv exists
    if os.path.exists("data/JEJU_ADDRESS.csv"):
        # Load the existing CSV
        address_df = pd.read_csv("data/JEJU_ADDRESS.csv", encoding="cp949")
        print("Loaded existing JEJU_ADDRESS.csv")
    else:
        # Create address_df from original data
        ori_df = pd.read_csv("data/JEJU_MCT_DATA.csv", encoding="cp949")
        address_df = ori_df[["ADDR"]].copy()
        address_df = address_df[~address_df["ADDR"].str.strip().eq("")]
        address_df["LATITUDE"] = None
        address_df["LONGITUDE"] = None
        print("Created new JEJU_ADDRESS.csv")

    null_longitude_count = address_df["LATITUDE"].isnull().sum()
    print(f"Number of rows with null LATITUDE: {null_longitude_count}")

    # Kakao geocoding function to get lat/lon
    def get_lat_lon_kakao(address):
        try:
            params = {"query": address}
            response = requests.get(kakao_url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["documents"]:
                    lat = data["documents"][0]["y"]  # latitude
                    lon = data["documents"][0]["x"]  # longitude
                    return float(lat), float(lon)
                else:
                    return None, None  # No results found
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None, None
        except Exception as e:
            print(f"Kakao API Error: {e}")
            return None, None

    # 실행
    for idx, row in tqdm(address_df.iterrows(), total=len(address_df)):
        if not row.isnull().any():  # Skip rows that already have lat/lon
            continue

        address = row["ADDR"]
        address = preprocess_address(address)

        lat, lon = get_lat_lon_kakao(address)

        address_df.at[idx, "LATITUDE"] = lat
        address_df.at[idx, "LONGITUDE"] = lon

        address_df.to_csv("data/JEJU_ADDRESS.csv", encoding="cp949", index=False)

        # if idx > 150:
        #     break


def add_address_googlemap():
    import googlemaps

    maps = googlemaps.Client(key=google_map_api_key)  # 구글맵 api 가져오기

    address_df = pd.read_csv("data/JEJU_ADDRESS.csv", encoding="cp949")
    # Remove columns with no name or starting with 'Unnamed'
    address_df = address_df.loc[
        :, ~address_df.columns.str.match("^Unnamed") & address_df.columns.notnull()
    ]

    null_latitude_count = address_df["LATITUDE"].isnull().sum()
    print(f"Number of rows with null Latitude: {null_latitude_count}")

    # 위도, 경도 반환하는 함수
    def get_lat_lon(address):
        try:
            location = maps.geocode(address)[0].get("geometry")
            # print(location)
            if location:
                return location["location"]["lat"], location["location"]["lng"]
            else:
                return None, None
        except Exception as e:
            print(e)
            return None, None

    # print(address_df.head(10))

    # 실행
    for idx, row in tqdm(address_df.iterrows(), total=len(address_df)):
        # print(row)
        if not row.isnull().any():
            continue

        address = row["ADDR"]
        address = preprocess_address(address)

        lat, lon = get_lat_lon(address)

        address_df.at[idx, "LATITUDE"] = lat
        address_df.at[idx, "LONGITUDE"] = lon

        address_df.to_csv("data/JEJU_ADDRESS.csv", encoding="cp949", index=False)

        # exit()
        # print(address_df[idx])

        # if idx > 1000:
        #     break


def edit_category():
    address_df = pd.read_csv("data/JEJU_ADDRESS.csv", encoding="cp949")
    address_df = address_df.rename(columns={"LATITIDE": "LATITUDE"})
    print(address_df.head(5))
    address_df.to_csv("data/JEJU_ADDRESS.csv", encoding="cp949", index=False)


if __name__ == "__main__":
    # Uncomment if you want to run Nominatim as well
    # get_address_nominatim()

    # Run the Kakao geocoding function
    # add_address_kakao()
    # add_address_googlemap()
    edit_category()
