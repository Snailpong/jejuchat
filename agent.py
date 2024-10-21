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
from utils.string_utils import clean_place_name, generate_naver_search_link

JEJU_MCT_DATA = pd.read_csv("data/JEJU_PROCESSED.csv", encoding="cp949")
PLACE = pd.read_csv("data/JEJU_PLACES_MERGED.csv", encoding="cp949")


class Agent:
    def __init__(self, api_key: str):
        self.model = get_model(api_key=api_key)

        self.state = "READY"
        self.input_dict = None
        self.previous_summary = []
        self.debug = False

    def set_state(self, state):
        self.state = state

    def set_input(self, input_dict):
        self.input_dict = input_dict

    def __call__(self):
        if self.state == "GET_QUESTION":
            self.process_input()
            return

        if self.state == "GEN_SQL":
            self.generate_sql()
            return

        if self.state == "FILTER_RESTAURANTS":
            self.filter_restaurants()
            return

        if self.state == "GENERATE_OK":
            response = self.generate_ok_answer()
            return response

        if self.state == "GENERATE_ERROR":
            response = self.generate_error_answer()
            return response

        else:
            self.state = "READY"
            return (
                "죄송해요. 처리 중에 문제가 생긴 것 같아요. 잠시 후 다시 시도해주세요."
            )

    def process_input(self):
        input_dict = self.input_dict
        use_current_location = input_dict["use_current_location"]
        user_question = input_dict["user_question"]
        if input_dict["use_current_location"]:
            pass
        self.log_debug("질문:\t", user_question)
        self.set_state("질문을 이해하고 있어요.")

        ca_result = self.analyze_context(input_dict)
        self.log_debug(ca_result)

        if (
            ca_result["result"] == "ok"
            and (not use_current_location)
            and ca_result["target_place"] == "HERE"
        ):
            self.error_message = "Current location-related information requires permission to access current location or time data. Please enable access."
            self.set_state("GENERATE_ERROR")
            return

        if ca_result["result"] != "ok":
            self.error_message = ca_result["error_message"]
            self.set_state("GENERATE_ERROR")
            return

        self.ca_result = ca_result

        self.set_state("GEN_SQL")

    def generate_sql(self):
        ca_result = self.ca_result

        processed_question = ca_result["processed_question"]

        single_question_prompt = make_single_question_prompt(processed_question)

        query_result = inference(single_question_prompt, self.model)
        self.log_debug(query_result)

        if query_result["result"] != "ok":
            self.error_message = query_result["error_message"]
            self.set_state("GENERATE_ERROR")
            return

        self.query_result = query_result
        self.set_state("FILTER_RESTAURANTS")

    def filter_restaurants(self):
        ca_result = self.ca_result
        query_result = self.query_result

        result_df = self.execute_query(query_result["query"])
        result_df = self.filter_duplicates(result_df)
        len_result_df = len(result_df)

        if result_df.empty:
            self.log_debug("조회된 결과가 없습니다.")
        else:
            self.log_debug(f"SQL 쿼리 결과가 {len_result_df} 개 조회되었어요")

        # If there is a target_place specified, calculate distance from target_place
        if ca_result["target_place"] != "NONE":
            result, result_df = self.calculate_distance_and_sort(
                ca_result["target_place"], result_df
            )

            if result != "ok":
                self.error_message = result
                self.set_state("GENERATE_ERROR")
                return

        self.log_debug(f"최종적으로 조건에 맞는 식당을 {len(result_df)}개 찾았어요.")
        self.log_debug(f"식당 리스트(최대 10개): {' '.join(result_df['MCT_NM'][:10])}")

        if len(result_df) == 0:
            self.error_message = "해당 조건에 맞는 식당이 0개로, 추천할 수 없었어요. 조건을 완화해보세요."
            self.set_state("GENERATE_ERROR")
            return

        # Check if there are more than 10 rows
        truncate_flag = False

        if len(result_df) > 10:
            truncate_flag = True

            if ca_result["shuffle"]:
                result_df = result_df.sample(10, random_state=42)
            else:
                result_df = result_df.head(10)

        self.truncate_flag = truncate_flag
        self.result_df = result_df

        self.set_state("GENERATE_OK")

    def generate_ok_answer(self):
        truncate_flag = self.truncate_flag
        result_df = self.result_df
        user_question = self.input_dict["user_question"]

        # Generate Naver search links and add them to result_df
        result_df["NAME_LINK"] = result_df.apply(
            lambda row: f"[{row['MCT_NM']}]({generate_naver_search_link(row['MCT_NM'], row['ADDR'])})",
            axis=1,
        )
        result_df = result_df.drop(columns=["MCT_NM", "ADDR"], errors="ignore")

        result_json = result_df.to_json(orient="records", force_ascii=False)

        final_prompt = self.prepare_final_prompt(
            user_question, result_json, truncate_flag
        )

        parsed_json = inference(final_prompt, self.model)

        # Print the response from the model
        self.log_debug("대답:", parsed_json["answer"])
        self.log_debug("요약:", parsed_json["summary"])

        self.update_previous_summary(parsed_json["summary"])
        self.state = "READY"

        return parsed_json["answer"]

    def generate_error_answer(self):
        user_question = self.input_dict["user_question"]
        error_message = self.error_message

        final_prompt = make_cannot_generate_sql_prompt(user_question, error_message)
        final_result = inference(final_prompt, self.model)
        self.log_debug("대답:", final_result)
        self.state = "READY"
        return final_result["answer"]

    def log_debug(self, *log):
        if self.debug:
            print(" ".join(map(str, log)))

    def get_previous_summary_str(self):
        if len(self.previous_summary) == 0:
            return "NONE"
        else:
            return "\n".join([f"{item}" for item in self.previous_summary])

    def analyze_context(self, input_dict):
        ca_prompt_question = make_context_analysis_prompt_question(
            user_question=input_dict["user_question"],
            use_current_location=input_dict["use_current_location"],
            weekday=input_dict["weekday"],
            hour=input_dict["hour"],
            previous_summary=self.get_previous_summary_str(),
        )
        ca_result = inference(ca_prompt_question, self.model)
        return ca_result

    def execute_query(self, sql_query):
        return ps.sqldf(sql_query, globals())

    def filter_duplicates(self, result_df):
        try:
            result_df = result_df.drop_duplicates(
                subset=["MCT_NM", "OP_YMD"], keep="first"
            )
        except Exception:
            self.log_debug("result_df.drop_duplicates failed")
        return result_df

    def calculate_distance_and_sort(self, target_place, result_df):
        place_lon, place_lat = None, None

        if target_place == "HERE":
            place_lat = self.input_dict["latitude"]
            place_lon = self.input_dict["longitude"]

        else:
            target_place = clean_place_name(target_place)
            self.log_debug("Try to find target place:", target_place)

            place_df = self.get_place_coordinates(target_place)

            if not place_df.empty:
                place_lat = place_df.iloc[0]["LATITUDE"]
                place_lon = place_df.iloc[0]["LONGITUDE"]

        if place_lon is None:
            error_message = (
                f"'{target_place}' 장소를 찾지 못했어요. 장소 이름을 다시 확인해주세요."
            )
            self.log_debug(error_message)
            return error_message, None

        self.log_debug("근처 식당 필터링을 수행합니다.", str(place_lat), str(place_lon))
        result_df["PLACE_DISTANCE"] = result_df.apply(
            lambda row: calculate_distance(
                place_lat, place_lon, row["LATITUDE"], row["LONGITUDE"]
            ),
            axis=1,
        )
        result_df = result_df[result_df["PLACE_DISTANCE"] < 5000]

        self.log_debug(f"거리 조건에 맞는 식당을 {len(result_df)}개 찾았어요.")
        result_df = result_df.sort_values(by="PLACE_DISTANCE").head(10)

        return "ok", result_df

    def get_place_coordinates(self, target_place):
        place_query = f"SELECT LATITUDE, LONGITUDE FROM PLACE WHERE PLACE_NAME = '{target_place}' LIMIT 1;"
        place_df = ps.sqldf(place_query, globals())

        if place_df.empty:
            self.log_debug("문자열이 일치하는 장소가 없어요. 포함 유사열로 시도할게요.")
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

    def update_previous_summary(self, summary):
        self.previous_summary.append(summary)
        if len(self.previous_summary) == 2:
            del self.previous_summary[0]

    def reset(self):
        self.previous_summary = []
