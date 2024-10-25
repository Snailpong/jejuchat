import urllib.parse

import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz


def naver_search(query: str) -> str:
    encoded_query = urllib.parse.quote(query)
    url = f"https://m.search.naver.com/search.naver?query={encoded_query}"
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def extract_name_href(html: str, selector: str) -> tuple:
    soup = BeautifulSoup(html, "html.parser")
    element = soup.select_one(selector)
    if element and element.has_attr("href"):
        return element.text.strip(), element["href"]
    return "", ""


def similarity(a: str, b: str) -> float:
    a = a.replace(" ", "")
    b = b.replace(" ", "")
    return fuzz.ratio(a, b)


def extract_place_url(query: str) -> str:
    address, name = query.split("/")
    query = address + " " + name

    result = naver_search(query)
    parsed = extract_name_href(html=result, selector="#_title > a")
    another = extract_name_href(
        html=result,
        selector="#loc-main-section-root > div > div.hx3zy > div:nth-child(2) > ul > li > div > div.ouxiq > a:nth-child(1)",
    )
    other = extract_name_href(
        html=result,
        selector="#loc-main-section-root > div > div.hx3zy > div:nth-child(2) > ul > li:nth-child(2) > div > div.ouxiq > a:nth-child(1)",
    )

    # Compare similarity between 'another' and 'other' with the query
    similarity_another = similarity(another[0], name)
    similarity_other = similarity(other[0], name)

    if similarity_another <= 20 and similarity_other <= 20:
        return (
            f"https://m.search.naver.com/search.naver?query={urllib.parse.quote(query)}"
        )
    if similarity_another > similarity_other:
        chosen = another
    else:
        chosen = other

    # Return the href of the more similar result
    return parsed[1] if parsed[1] else chosen[1]
