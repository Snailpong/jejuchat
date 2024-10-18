
def parse_json_from_str(json_str):
    import json
    import re

    # Extract the content between curly braces
    match = re.findall(r"\{.*?\}", json_str, re.DOTALL)[0]

    # Parse the JSON content
    parsed_json = json.loads(match)
    return parsed_json

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