import os
import random
from datetime import datetime

import streamlit as st

from agent import Agent
from questions.example_question import app_question_list
from utils.codes import STATE_CODE_DICT

if "agent" not in st.session_state:
    if api_key := os.getenv("GOOGLE_API_KEY"):
        pass
    else:
        from utils.api_key import google_ai_studio_api_key  # type: ignore

        api_key = google_ai_studio_api_key

    st.session_state.agent = Agent(api_key=api_key)

agent = st.session_state.agent

st.set_page_config(page_title="제주 맛집 추천 챗봇 🍊")

# Replicate Credentials
with st.sidebar:
    with st.expander("현재 정보 활용 설정", expanded=True):
        use_current_location_time = st.checkbox("현재 정보 활용")
        latitude = st.number_input("위도", format="%.6f", value=33.558277)
        longitude = st.number_input("경도", format="%.6f", value=126.75978)

        user_date = st.date_input("오늘 날짜", value=datetime.now())
        user_time = st.time_input("현재 시간", value=datetime.now())
    devmode = st.checkbox("dev 모드 (SQL쿼리 출력)")


TITLE = "제주 맛집 추천 챗봇 🍊"
ONBOARD_MESSAGE = "**다음과 같은 질문을 할 수 있어요.👇 참고해서 질문해 주세요! 🧑‍🍳**"
FIRST_MESSAGE = "혼저 옵서예! 👋 제주 맛집 추천 챗봇이에요. 🍊 \n\n고민하지 마시고 질문해주시면 성심성의껏 찾아드릴게요! 💪"

st.title(TITLE)


def onboarding_chat():
    st.markdown(ONBOARD_MESSAGE)

    for question in st.session_state.random_questions:
        if st.button(question) and agent.state == "READY":
            st.session_state.messages.append({"role": "user", "content": question})


if "messages" not in st.session_state.keys():
    if "random_questions" not in st.session_state.keys():
        st.session_state.random_questions = random.sample(app_question_list, 4)

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": FIRST_MESSAGE,
        }
    ]

# Display or clear chat messages
onboarding_chat()
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def clear_chat_history():
    agent.reset()
    st.session_state.messages = [
        {"role": "assistant", "content": "어드런 식당 찾으시쿠과?"}
    ]


st.sidebar.button("Clear Chat History", on_click=clear_chat_history)


# User-provided prompt
if prompt := st.chat_input():  # (disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    agent.debug = devmode

    input_dict = {
        "use_current_location_time": use_current_location_time,
        "user_question": st.session_state.messages[-1],
        "weekday": None,
        "hour": None,
    }
    if use_current_location_time:
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][user_date.weekday()]
        current_info = {
            "weekday": weekday,
            "hour": user_time.hour,
            "latitude": latitude,
            "longitude": longitude,
        }
        input_dict.update(current_info)

    with st.chat_message("assistant"):
        agent.set_state("GET_QUESTION")
        agent.set_input(input_dict)
        while agent.state != "READY":
            with st.spinner(STATE_CODE_DICT[agent.state]):
                response = agent()

        if devmode:
            try:
                query = agent.query_result["query"]
                response = f"SQL 쿼리: `{query}`\n\n{response}"
            except Exception as _:
                pass

        st.markdown(response)

    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
