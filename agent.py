import pandas as pd
import pandasql as ps

from prompts import (
    make_cannot_generate_sql_prompt,
    make_context_analysis_prompt_question,
    make_single_question_prompt,
    make_single_result_prompt,
)
from utils.geo_utils import calculate_distance
from utils.inference_utils import get_model, inference
from utils.string_utils import clean_place_name

JEJU_MCT_DATA = pd.read_csv("data/JEJU_PROCESSED.csv", encoding="cp949")
PLACE = pd.read_csv("data/JEJU_PLACES_MERGED.csv", encoding="cp949")


class Agent:
    def __init__(self):
        self.model = get_model()
        self.previous_summary = []
        pass

    def __call__(self, input_dict, debug=False):
        use_current_location_time = input_dict["use_current_location_time"]
        user_question = input_dict["user_question"]
        if input_dict["use_current_location_time"]:
            pass

        if debug:
            print("질문:\t", user_question)

        ca_prompt_question = make_context_analysis_prompt_question(**input_dict)
        ca_result = inference(ca_prompt_question, self.model)

        print(use_current_location_time, ca_result["target_place"])

        if (not use_current_location_time) and ca_result["target_place"] != "NONE":
            ca_result["result"] = "error"
            ca_result["error_message"] = (
                "Current location-related information requires permission to access current location or time data. Please enable access."
            )

        if ca_result["result"] != "ok":
            # Final prompt for error, including the question and reason why it's not valid
            final_prompt = make_cannot_generate_sql_prompt(
                user_question, ca_result["error_message"]
            )

            # 모델을 통해 답을 생성
            final_result = inference(final_prompt, self.model)

            print("대답:", final_result)
            return

        processed_question = ca_result["processed_question"]
        target_place = ca_result["target_place"]

        single_question_prompt = make_single_question_prompt(processed_question)

        query_result = inference(single_question_prompt, self.model)
        print(query_result)

        # Extract the SQL query from the parsed JSON
        if query_result["result"] != "ok":
            # Final prompt for error, including the question and reason why it's not valid
            final_prompt = make_cannot_generate_sql_prompt(
                user_question, query_result["error_message"]
            )

            # 모델을 통해 답을 생성
            final_result = inference(final_prompt, self.model)

            print("대답:", final_result)
            return

        sql_query = query_result["query"]

        # print("생성된 쿼리:\t", sql_query)

        # Execute the SQL query on the DataFrame
        result_df = ps.sqldf(sql_query, globals())

        # YM 컬럼을 제외하고 MCT_NM, OP_YMD 기준으로 중복 제거
        try:
            result_df = result_df.drop_duplicates(
                subset=["MCT_NM", "OP_YMD"], keep="first"
            )
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
        if len(self.previous_summary) == 0:
            previous_summary_str = "NONE"
        else:
            previous_summary_str = "\n".join(
                [f"- {item}" for item in self.previous_summary[:-1]] + ["- Latest"]
            )

        final_prompt = make_single_result_prompt(
            user_question, result_json, previous_summary_str
        )

        if truncate_flag:
            final_prompt = (
                final_prompt
                + "\nNote: The result contains more than 10 entries. Only 10 have been shown randomly."
            )

        parsed_json = inference(final_prompt, self.model)

        # Print the response from the model
        print("대답:", parsed_json["answer"])
        print("요약:", parsed_json["summary"])

        return parsed_json["answer"]

    def reset(self):
        self.previous_summary = []
