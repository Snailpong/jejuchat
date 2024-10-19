import google.generativeai as genai
import pandas as pd
import pandasql as ps

from prompts import (
    make_cannot_generate_sql_prompt,
    make_context_analysis_prompt_question,
    make_single_question_prompt,
    make_single_result_prompt,
)
from questions import valid_question_list
from utils.api_key import google_ai_studio_api_key
from utils.geo_utils import calculate_distance
from utils.inference_utils import inference
from utils.string_utils import clean_place_name, count_prompt_token, parse_json_from_str

genai.configure(api_key=google_ai_studio_api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# CSV 파일 로드
JEJU_MCT_DATA = pd.read_csv("data/JEJU_PROCESSED.csv", encoding="cp949")
PLACE = pd.read_csv("data/JEJU_PLACES_MERGED.csv", encoding="cp949")

previous_summary = []


def generate_content(prompt):
    return model.generate_content(prompt, safety_settings="BLOCK_ONLY_HIGH")


def get_reply_from_question(question_dict):
    question = question_dict["question"]
    query = question_dict["query"]

    print("질문:\t", question)
    print("챗지 쿼리:\t", query)

    ca_prompt_question = make_context_analysis_prompt_question(question)
    ca_result = inference(ca_prompt_question, model)
    print(ca_result)

    if ca_result["result"] != "ok":
        # Final prompt for error, including the question and reason why it's not valid
        final_prompt = make_cannot_generate_sql_prompt(
            question, ca_result["error_message"]
        )

        # 모델을 통해 답을 생성
        final_result = inference(final_prompt, model)

        print("대답:", final_result)
        return

    processed_question = ca_result["processed_question"]
    target_place = ca_result["target_place"]

    single_question_prompt = make_single_question_prompt(processed_question)

    query_result = inference(single_question_prompt, model)
    print(query_result)

    # Extract the SQL query from the parsed JSON
    if query_result["result"] != "ok":
        # Final prompt for error, including the question and reason why it's not valid
        final_prompt = make_cannot_generate_sql_prompt(
            question, query_result["error_message"]
        )

        # 모델을 통해 답을 생성
        final_result = inference(final_prompt, model)

        print("대답:", final_result)
        return

    sql_query = query_result["query"]

    # print("생성된 쿼리:\t", sql_query)

    # Execute the SQL query on the DataFrame
    result_df = ps.sqldf(sql_query, globals())

    # YM 컬럼을 제외하고 MCT_NM, OP_YMD 기준으로 중복 제거
    try:
        result_df = result_df.drop_duplicates(subset=["MCT_NM", "OP_YMD"], keep="first")
    except Exception:
        pass

    # Print the result
    len_result_df = len(result_df)

    if result_df.empty:
        print("조회된 결과가 없습니다.")
    else:
        print(len_result_df, "개 조회됨: ", ", ".join(result_df["MCT_NM"][:10]))

    # If there is a target_place specified, calculate distance from target_place
    if target_place != "NONE":
        target_place = clean_place_name(target_place)
        print("Try to find target place:", target_place)

        # Fetch the latitude and longitude of the target_place from the PLACE table
        place_query = f"SELECT LATITUDE, LONGITUDE FROM PLACE WHERE PLACE_NAME = '{target_place}' LIMIT 1;"
        place_df = ps.sqldf(place_query, globals())

        if not place_df.empty:
            print("Exact place found.")
        if place_df.empty:
            print(
                "Exact place not found. Try to find the most similar place containing the target_place."
            )
            # If the exact place is not found, try to find the most similar place containing the target_place
            place_query = f"SELECT LATITUDE, LONGITUDE FROM PLACE WHERE PLACE_NAME LIKE '%{target_place}%' LIMIT 1;"
            place_df = ps.sqldf(place_query, globals())

            if not place_df.empty:
                print("Similar place found.")

        if not place_df.empty:
            place_lat = place_df.iloc[0]["LATITUDE"]
            place_lon = place_df.iloc[0]["LONGITUDE"]

            # Calculate the distance for each row in the result_df
            result_df["PLACE_DISTANCE"] = result_df.apply(
                lambda row: calculate_distance(
                    place_lat, place_lon, row["LATITUDE"], row["LONGITUDE"]
                ),
                axis=1,
            )
            # Remove rows where PLACE_DISTANCE is 5000 or more
            result_df = result_df[result_df["PLACE_DISTANCE"] < 5000]

            # Sort the result by distance
            result_df = result_df.sort_values(by="PLACE_DISTANCE")

            # Keep only the 10 closest places
            result_df = result_df.head(10)
            len_result_df = len(result_df)
        else:
            print(f"Target place '{target_place}' not found in the PLACE table.")

    # Check if there are more than 10 rows
    truncate_flag = False

    if len(result_df) > 10:
        truncate_flag = True
        result_df = result_df.sample(10, random_state=42)  # Randomly sample 10 rows

    result_json = result_df.to_json(orient="records", force_ascii=False)
    # final_prompt = result_prompt_format.format(question, result_json)

    # Convert previous_summary list to a string with bullet points
    if len(previous_summary) == 0:
        previous_summary_str = "NONE"
    else:
        previous_summary_str = "\n".join(
            [f"- {item}" for item in previous_summary[:-1]] + ["- Latest"]
        )

    final_prompt = make_single_result_prompt(
        question, result_json, previous_summary_str
    )

    if truncate_flag:
        final_prompt = (
            final_prompt
            + "\nNote: The result contains more than 10 entries. Only 10 have been shown randomly."
        )
    # 모델을 통해 답을 생성
    response = generate_content(final_prompt)
    parse_json = parse_json_from_str(response.text)

    # Print the response from the model
    print("대답:", parse_json["answer"])
    print("요약:", parse_json["summary"])


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
    from prompts.sql_prompt import sql_generation_prompt

    count_prompt_token(model, sql_generation_prompt)
    # manual_question()
    terminal_question()
