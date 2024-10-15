import json
import re

import google.generativeai as genai
import pandas as pd
import pandasql as ps

from prompts import (result_prompt_format, single_question_prompt_format,
                     sql_generation_prompt)
from questions import ex_question_list, valid_question_list
from utils.api_key import google_ai_studio_api_key

genai.configure(api_key=google_ai_studio_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# CSV 파일 로드
JEJU_MCT_DATA = pd.read_csv("data/JEJU_PROCESSED.csv", encoding="cp949")


def count_prompt_token():
    response = model.count_tokens(sql_generation_prompt)
    print(f"Prompt Token Count: {response.total_tokens}")


def make_single_question_prompt(single_question):
    return (
        sql_generation_prompt
        + "\n"
        + single_question_prompt_format.format(single_question)
    )


def get_reply_from_question(single_question):
    print("질문:", single_question)

    # GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    # genai.configure(api_key=GOOGLE_API_KEY)

    # question = ex_question_list[0]
    single_question_prompt = make_single_question_prompt(single_question)

    response = model.generate_content(single_question_prompt)

    # Extract the content between curly braces
    match = re.findall(r"\{.*?\}", response.text, re.DOTALL)[0]

    # Parse the JSON content
    parsed_json = json.loads(match)

    # Extract the SQL query from the parsed JSON
    sql_query = parsed_json["query"]

    print("SQL 입력 쿼리:", sql_query)

    # Execute the SQL query on the DataFrame
    result_df = ps.sqldf(sql_query, globals())

    # Print the result
    print(result_df)

    result_json = result_df.to_json(orient="records", force_ascii=False)
    final_prompt = result_prompt_format.format(single_question, result_json)

    # 모델을 통해 답을 생성
    response = model.generate_content(final_prompt)

    # Print the response from the model
    print("대답:", response.text)


if __name__ == "__main__":
    count_prompt_token()

    # single_question = "제주시 연동에 있는 분식 전문점 중 이용금액이 상위 25%에 속하는 곳 중 현지인 비중이 제일 낮은 곳은?"
    # single_question = "가게명에 솥뚜껑이 들어간 곳 중 여성 회원 비중이 가장 높은 곳은?"
    single_question = "가게명에 솥뚜껑이 들어간 곳 중 여성 회원 비중이 가장 높은 곳은?"
    # single_question = "제주도 치킨집 중 가장 오래된 곳은?"

    get_reply_from_question(single_question)

    # for i in range(5):
    #     get_reply_from_question(valid_question_list[i]["question"])
    #     print()
