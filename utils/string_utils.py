def parse_json_from_str(json_str):
    import json
    import re

    def clean_json_trailing_commas(json_str):
        # This regex looks for trailing commas before the closing brace or bracket and removes them
        return re.sub(r",\s*(?=[}\]])", "", json_str)

    try:
        # Extract the content between curly braces
        match = re.findall(r"\{.*?\}", json_str, re.DOTALL)[0]

        # Clean trailing commas in the matched JSON string
        cleaned_json_str = clean_json_trailing_commas(match)

        # Parse the cleaned JSON content
        parsed_json = json.loads(cleaned_json_str)
        return parsed_json

    except (json.JSONDecodeError, IndexError) as e:
        print(f"Failed to parse JSON: {e}")
        return None


def count_prompt_token(model, prompt):
    response = model.count_tokens(prompt)
    return response.total_tokens


def clean_place_name(place_name):
    import re

    # Remove content inside parentheses (including the parentheses)
    if isinstance(place_name, str):  # Check if the value is a string
        place_name = re.sub(r"\(.*?\)", "", place_name)

        # Remove whitespace, commas, and periods
        place_name = re.sub(r"[,\.\s]+", "", place_name)

    return place_name


def generate_naver_search_link(store_name, address):
    search_query = f"{address} {store_name}"
    search_query_encoded = search_query.replace(" ", "+")  # Replace spaces with "+"
    naver_search_url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_sly.hst&fbm=0&acr=1&ie=utf8&query={search_query_encoded}"
    return naver_search_url
