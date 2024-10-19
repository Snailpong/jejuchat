def inference(prompt, model, return_json=True):
    from utils.string_utils import parse_json_from_str

    response = model.generate_content(prompt, safety_settings="BLOCK_ONLY_HIGH")

    if return_json:
        response = parse_json_from_str(response.text)

    return response
