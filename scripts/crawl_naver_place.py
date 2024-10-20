import urllib.parse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

tqdm.pandas()


def naver_search(query: str) -> str:
    encoded_query = urllib.parse.quote(query)
    url = f"https://m.search.naver.com/search.naver?query={encoded_query}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def extract_href(html: str, selector: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    element = soup.select_one(selector)
    return element["href"] if element and element.has_attr("href") else ""


def extract_place_name(query: str) -> str:
    result = naver_search(query)
    parsed = extract_href(html=result, selector="#_title > a")
    another = extract_href(
        html=result,
        selector="#loc-main-section-root > div > div.hx3zy > div:nth-child(2) > ul > li > div > div.ouxiq > a:nth-child(1)",
    )
    return parsed if parsed else another


if __name__ == "__main__":
    import pandas as pd

    df = pd.read_csv("data/JEJU_PROCESSED.csv", encoding="cp949")
    df = df.drop_duplicates(subset=["MCT_NM", "OP_YMD_x"], keep="first")
    df["NAVER_PLACE_URL"] = (df["ADDR"] + " " + df["MCT_NM"]).progress_map(
        extract_place_name
    )

    df.to_csv("place.csv", index=False)
