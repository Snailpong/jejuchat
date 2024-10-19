single_question_input_format = """
    "natural_language_question": "{natural_language_question}",
    "use_current_location_time": "{use_current_location_time}",
    "weekday_hour": "{weekday_hour}",
    "previous_conversation_summary": "{previous_conversation_summary}"
"""


def make_single_question_json(single_question_input):
    return (
        """Single Question:
Input:
{"""
        + single_question_input
        + """
}
Output:"""
    )


def make_single_question_prompt(
    single_question,
    use_current_location_time="FALSE",
    weekday_hour="NONE",
    previous_conversation_summary="NONE",
):
    from prompts.sql_prompt import sql_generation_prompt

    single_question_input = single_question_input_format.format(
        natural_language_question=single_question,
        use_current_location_time=use_current_location_time,
        weekday_hour=weekday_hour,
        previous_conversation_summary=previous_conversation_summary,
    )
    single_question_prompt = make_single_question_json(single_question_input)

    return sql_generation_prompt + "\n" + single_question_prompt
