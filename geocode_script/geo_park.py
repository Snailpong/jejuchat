import re

import pandas as pd
from tqdm import tqdm

from utils.api_key import google_map_api_key


def preprocess_address(address):
    # Remove "제주특별자치도"
    address = address.replace("제주특별자치도", "").strip()

    # Remove everything after the first comma
    if "," in address:
        address = address.split(",")[0].strip()

    # Remove anything that starts with "외" (e.g., "외 2필지")
    address = re.sub(r"외.*", "", address).strip()

    # Remove full words ending in "읍" or "면" (e.g., "한림읍", "애월읍")
    # address = re.sub(r"\S*읍|\S*면", "", address).strip()
    return address


def get_adddress_nominatim():
    from geopy.geocoders import Nominatim

    ori_df = pd.read_csv("data/제주특별자치도_제주시_주차장정보_20240724.csv")
    ori_df_2 = pd.read_csv("data/제주특별자치도_서귀포시_주차장정보_20240712.csv")

    ori_df = pd.concat([ori_df, ori_df_2], axis=0)

    address_df = ori_df[["주차장명", "소재지지번주소"]].copy()
    address_df.columns = ["PARKING_NAME", "ADDR"]

    geolocator = Nominatim(user_agent="South Korea")

    # 위도, 경도 반환하는 함수
    def get_lat_lon(address):
        try:
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude
            else:
                return None, None
        except Exception:
            return None, None

    address_df["Latitude"] = None
    address_df["Longitude"] = None

    # print(address_df.head(10))

    # 실행
    for idx, row in tqdm(address_df.iterrows(), total=len(address_df)):
        address = row["ADDR"]
        address = preprocess_address(address)

        lat, lon = get_lat_lon(address)

        address_df.at[idx, "Latitude"] = lat
        address_df.at[idx, "Longitude"] = lon

        address_df.to_csv("data/JEJU_PARKING.csv", encoding="cp949", index=False)

    # if idx == 100:
    #     break


def add_address_googlemap():
    import googlemaps

    maps = googlemaps.Client(key=google_map_api_key)  # 구글맵 api 가져오기

    address_df = pd.read_csv("data/JEJU_PARKING.csv", encoding="cp949")
    # Remove columns with no name or starting with 'Unnamed'
    address_df = address_df.loc[
        :, ~address_df.columns.str.match("^Unnamed") & address_df.columns.notnull()
    ]

    address_df["Latitude"] = None
    address_df["Longitude"] = None

    null_latitude_count = address_df["Latitude"].isnull().sum()
    print(f"Number of rows with null Latitude: {null_latitude_count}")
    # exit()

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

        address_df.at[idx, "Latitude"] = lat
        address_df.at[idx, "Longitude"] = lon

        address_df.to_csv("data/JEJU_ADDRESS.csv", encoding="cp949", index=False)

        # exit()
        # print(address_df[idx])

        # if idx > 1000:
        #     break


if __name__ == "__main__":
    # get_adddress_nominatim()
    add_address_googlemap()
