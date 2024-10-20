from agent import Agent
from questions import valid_question_list
from utils.inference_utils import get_model
from utils.string_utils import count_prompt_token

model = get_model()
agent = Agent()


def get_reply_from_question(question_dict):
    question = question_dict["question"]
    query = question_dict["query"]

    input_dict = {"user_question": question, "use_current_location_time": False}

    response = agent(input_dict, debug=True)
    return


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
