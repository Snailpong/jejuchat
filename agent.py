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

        ca_result = self.analyze_context(input_dict)

        print(use_current_location_time, ca_result["target_place"])

        if (not use_current_location_time) and ca_result["target_place"] != "NONE":
            return self.handle_error(
                user_question,
                "Current location-related information requires permission to access current location or time data. Please enable access.",
            )

        if ca_result["result"] != "ok":
            return self.handle_error(user_question, ca_result["error_message"])

        processed_question = ca_result["processed_question"]

        single_question_prompt = make_single_question_prompt(processed_question)

        query_result = inference(single_question_prompt, self.model)
        print(query_result)

        if query_result["result"] != "ok":
            return self.handle_error(user_question, query_result["error_message"])

        result_df = self.execute_query(query_result["query"])
        result_df = self.filter_duplicates(result_df)
        len_result_df = len(result_df)

        if result_df.empty:
            print("조회된 결과가 없습니다.")
        else:
            print(len_result_df, "개 조회됨: ", ", ".join(result_df["MCT_NM"][:10]))

        # If there is a target_place specified, calculate distance from target_place
        if ca_result["target_place"] != "NONE":
            result_df = self.calculate_distance_and_sort(
                ca_result["target_place"], result_df
            )

        # Check if there are more than 10 rows
        truncate_flag = False

        if len(result_df) > 10:
            truncate_flag = True

            if ca_result["shuffle"]:
                result_df = result_df.sample(10, random_state=42)
            else:
                result_df = result_df.head(10)

        result_json = result_df.to_json(orient="records", force_ascii=False)

        final_prompt = self.prepare_final_prompt(
            user_question, result_json, truncate_flag
        )

        parsed_json = inference(final_prompt, self.model)

        # Print the response from the model
        print("대답:", parsed_json["answer"])
        print("요약:", parsed_json["summary"])

        return parsed_json["answer"]

    def get_previous_summary_str(self):
        # Convert previous_summary list to a string with bullet points
        if len(self.previous_summary) == 0:
            return "NONE"
        else:
            return "\n".join(
                [f"- {item}" for item in self.previous_summary[:-1]] + ["- Latest"]
            )

    def analyze_context(self, input_dict):
        ca_prompt_question = make_context_analysis_prompt_question(
            previous_summary=self.get_previous_summary_str(), **input_dict
        )
        ca_result = inference(ca_prompt_question, self.model)
        return ca_result

    def handle_error(self, user_question, error_message):
        final_prompt = make_cannot_generate_sql_prompt(user_question, error_message)
        final_result = inference(final_prompt, self.model)
        print("대답:", final_result)
        return final_result

    def execute_query(self, sql_query):
        return ps.sqldf(sql_query, globals())

    def filter_duplicates(self, result_df):
        try:
            result_df = result_df.drop_duplicates(
                subset=["MCT_NM", "OP_YMD"], keep="first"
            )
        except Exception:
            pass
        return result_df

    def calculate_distance_and_sort(self, target_place, result_df):
        target_place = clean_place_name(target_place)
        print("Try to find target place:", target_place)

        place_df = self.get_place_coordinates(target_place)

        if not place_df.empty:
            place_lat = place_df.iloc[0]["LATITUDE"]
            place_lon = place_df.iloc[0]["LONGITUDE"]

            result_df["PLACE_DISTANCE"] = result_df.apply(
                lambda row: calculate_distance(
                    place_lat, place_lon, row["LATITUDE"], row["LONGITUDE"]
                ),
                axis=1,
            )
            result_df = result_df[result_df["PLACE_DISTANCE"] < 5000]
            result_df = result_df.sort_values(by="PLACE_DISTANCE").head(10)
        else:
            print(f"Target place '{target_place}' not found in the PLACE table.")

        return result_df

    def get_place_coordinates(self, target_place):
        place_query = f"SELECT LATITUDE, LONGITUDE FROM PLACE WHERE PLACE_NAME = '{target_place}' LIMIT 1;"
        place_df = ps.sqldf(place_query, globals())

        if place_df.empty:
            print("Exact place not found. Trying to find a similar place.")
            place_query = f"SELECT LATITUDE, LONGITUDE FROM PLACE WHERE PLACE_NAME LIKE '%{target_place}%' LIMIT 1;"
            place_df = ps.sqldf(place_query, globals())

        return place_df

    def prepare_final_prompt(self, user_question, result_json, truncate_flag):
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
            final_prompt += "\nNote: The result contains more than 10 entries. Only 10 have been shown."

        return final_prompt

    def reset(self):
        self.previous_summary = []
