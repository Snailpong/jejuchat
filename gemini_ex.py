import json
import re

import google.generativeai as genai
import pandas as pd
import pandasql as ps

from prompts import (result_prompt_format, single_question_input_format, make_single_question_json,
                     sql_generation_prompt)
from questions import ex_question_list, valid_question_list
from utils.api_key import google_ai_studio_api_key

genai.configure(api_key=google_ai_studio_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# CSV 파일 로드
JEJU_MCT_DATA = pd.read_csv("data/JEJU_PROCESSED.csv", encoding="cp949")
PLACE = pd.read_csv("data/JEJU_PLACES_MERGED.csv", encoding="cp949")


def count_prompt_token():
    response = model.count_tokens(sql_generation_prompt)
    print(f"Prompt Token Count: {response.total_tokens}")


def make_single_question_prompt(single_question):
    single_question_input = single_question_input_format.format(
            natural_language_question=single_question,
            use_current_location_time="FALSE",
            weekday_hour="NONE",
            previous_conversation_summary="NONE"
            )
    single_question_prompt = make_single_question_json(single_question_input)
    
    return (
        sql_generation_prompt
        + "\n"
        + single_question_prompt
    )

def generate_content(prompt):
    return model.generate_content(prompt, safety_settings="BLOCK_ONLY_HIGH")


def get_reply_from_question(question_dict):
    question = question_dict["question"]
    query = question_dict["query"]

    print("질문:\t", question)
    print("챗지 쿼리:\t", query)

    single_question_prompt = make_single_question_prompt(question)

    response = generate_content(single_question_prompt)

    # Extract the content between curly braces
    match = re.findall(r"\{.*?\}", response.text, re.DOTALL)[0]

    # Parse the JSON content
    parsed_json = json.loads(match)

    # Extract the SQL query from the parsed JSON
    if parsed_json["result"] == "error":
        from prompts import cannot_generate_sql_prompt_format
        print(parsed_json)

        # Final prompt for error, including the question and reason why it's not valid
        final_prompt =cannot_generate_sql_prompt_format.format(question=question, error_message=parsed_json["error_message"])
        
        # 모델을 통해 답을 생성
        response = model.generate_content(final_prompt)

        # Print the response from the model
        print("대답:", response.text)
        return


    sql_query = parsed_json["query"]

    # print("생성된 쿼리:\t", sql_query)
    print(parsed_json)

    # Execute the SQL query on the DataFrame
    result_df = ps.sqldf(sql_query, globals())

    # YM 컬럼을 제외하고 MCT_NM, OP_YMD 기준으로 중복 제거
    result_df = result_df.drop_duplicates(subset=['MCT_NM', 'OP_YMD'], keep='first')

    # Check if there are more than 10 rows
    truncate_flag = False
    len_result_df = len(result_df)
    if len(result_df) > 10:
        truncate_flag = True
        result_df = result_df.sample(10, random_state=42)  # Randomly sample 10 rows

    # Print the result
    if result_df.empty:
        print("조회된 결과가 없습니다.")
    elif len(result_df) == 1:
        print(result_df.to_json(orient="records", force_ascii=False))
    else:
        print(len_result_df,"개 조회됨: ",", ".join(result_df['MCT_NM']))


    result_json = result_df.to_json(orient="records", force_ascii=False)
    # final_prompt = result_prompt_format.format(question, result_json)

    if truncate_flag:
        final_prompt = result_prompt_format.format(question=question, result_json=result_json) + \
                       "\nNote: The result contains more than 10 entries. Only 10 have been shown randomly."
    else:
        final_prompt = result_prompt_format.format(question=question, result_json=result_json) 

    # 모델을 통해 답을 생성
    response = generate_content(final_prompt)

    # Print the response from the model
    print("대답:", response.text)

def manual_question():
    # single_question = "제주시 연동에 있는 분식 전문점 중 이용금액이 상위 25%에 속하는 곳 중 현지인 비중이 제일 낮은 곳은?"
    # single_question = "가게명에 솥뚜껑이 들어간 곳 중 여성 회원 비중이 가장 높은 곳은?"
    # single_question = "가게명에 솥뚜껑이 들어간 곳 중 여성 회원 비중이 가장 높은 곳은?"
    # single_question = "제주도 치킨집 중 가장 오래된 곳은?"
    # single_question_dict = {"question": "내일 이호우테해수욕장 근처 관광지 가려 하는데 추천해줘", "query": "-"}
    # single_question_dict = {"question": "내일 음침한 곳 가려고 추천해줘", "query": "-"}
    # single_question_dict = {"question": "내일 커피 마시러 갈건데 추천해줘!", "query": "-"}
    # single_question_dict = {"question": "오메기떡이 먹고 싶은데 추천해줘!", "query": "-"}
    # single_question_dict = {"question": "흑돼지 먹고 싶은데 가게 추천해줘!", "query": "-"}
    # single_question_dict = {"question": "제주 시내에서 저녁에 고기 먹으러 갈 건데 가게 추천해줘!", "query": "-"}
    # single_question_dict = {"question": "2023년 5월 기준으로 제주시 치킨집 중 20대 비중이 가장 높은 곳은?", "query": "-"}
    # single_question_dict = {"question": "가게 이름에 차돌박이 이 포함된 곳들 추천해줘", "query": "-"}
    # single_question_dict = {"question": "고기국수 먹고 싶은데 가게 추천해줘!", "query": "-"}

    # get_reply_from_question(single_question_dict)
    # get_reply_from_question({"question": "오늘의 제주도 날씨는?", "query": "-"})
    # get_reply_from_question({"question": "오늘 여는 흑돼지집 추천해줘", "query": "-"})
    # exit()

    # for i in range(6):
    for i in range(7, 10):
        print("Question", i + 1)
        get_reply_from_question(valid_question_list[i])
        print()

def terminal_question():
    cnt = 1
    while True:
        print("Question", cnt)

        try:
            question = input("질문을 입력하세요: ")
        except UnicodeDecodeError as e:
            print(f"입력 처리 중 오류 발생: {e}")
            continue
        
        get_reply_from_question({"question": question, "query": "-"})
        print()
        cnt += 1
    


if __name__ == "__main__":
    count_prompt_token()
    # manual_question()
    terminal_question()

    
