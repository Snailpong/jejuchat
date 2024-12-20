def get_model(api_key: str = None):
    import google.generativeai as genai

    if api_key is None:
        from utils.api_key import google_ai_studio_api_key

        api_key = google_ai_studio_api_key

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    return model


def inference(prompt, model, return_json=True):
    from utils.string_utils import parse_json_from_str

    response = model.generate_content(prompt, safety_settings="BLOCK_NONE")

    if return_json:
        response = parse_json_from_str(response.text)

    return response
