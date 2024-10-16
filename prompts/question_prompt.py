single_question_input_format = """
    "natural_language_question": "{natural_language_question}",
    "use_current_location_time": "{use_current_location_time}",
    "weekday_hour": "{weekday_hour}",
    "previous_conversation_summary": "{previous_conversation_summary}"
"""

def make_single_question_json(single_question_input):
    return """Single Question:
Input: 
{""" + single_question_input + """
}
Output:"""