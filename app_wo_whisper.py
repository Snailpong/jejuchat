import os
import random
from datetime import datetime

import streamlit as st

from agent import Agent
from questions.example_question import app_question_list
from utils.codes import STATE_CODE_DICT

TITLE = "제주 맛집 추천 챗봇 🍊"
ONBOARD_MESSAGE = (
    "**다음과 같은 질문을 할 수 있어요. 👇**   \n\n**참고해서 질문해 주세요! 🧑‍🍳**"
)
FIRST_MESSAGE = "혼저 옵서예! 👋 제주 맛집 추천 챗봇이에요. 🍊 \n\n고민하지 마시고 질문해주시면 성심성의껏 찾아드릴게요! 💪"


def add_user_message(text):
    st.session_state.messages.append({"role": "user", "content": text})
    st.rerun()


def onboarding_chat():
    with st.chat_message("assistant"):
        st.write(FIRST_MESSAGE)
    with st.chat_message("assistant"):
        st.write(ONBOARD_MESSAGE)

    for question in st.session_state.random_questions:
        cols = st.columns([0.05, 0.95])
        with cols[1]:
            if st.button(question) and agent.state == "READY":
                agent.set_state("ONBOARD_BUTTON")
                st.session_state.messages.append({"role": "user", "content": question})


# Clear chat history button
def clear_chat_history():
    agent.reset()
    st.session_state.messages = []


if "agent" not in st.session_state:
    if api_key := os.getenv("GOOGLE_API_KEY"):
        pass
    else:
        from utils.api_key import google_ai_studio_api_key

        api_key = google_ai_studio_api_key
    st.session_state.agent = Agent(api_key=api_key)

agent = st.session_state.agent


st.set_page_config(page_title="제주 맛집 추천 챗봇 🍊")

# Sidebar for location and settings
with st.sidebar:
    with st.expander("현재 정보 활용 설정", expanded=True):
        use_current_location = st.checkbox("현재 위치 정보 활용")
        latitude = st.number_input("위도", format="%.6f", value=33.558277)
        longitude = st.number_input("경도", format="%.6f", value=126.75978)
        user_date = st.date_input("오늘 날짜", value=datetime.now())
        user_time = st.time_input("현재 시간", value=datetime.now())
    devmode = st.checkbox("dev 모드 (SQL쿼리 출력)")
    st.button("Clear Chat History", on_click=clear_chat_history)

# App title and introductory message
st.title(TITLE)

# Load initial sample questions
if "random_questions" not in st.session_state:
    st.session_state.random_questions = random.sample(app_question_list, 4)

# Display onboarding message
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None

# Display chat history
onboarding_chat()
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Main input area with text and audio input options
if prompt := st.chat_input(placeholder="내용을 입력해주세요"):
    agent.set_state("CHAT")
    add_user_message(prompt)

# Process the last user message if it’s new
if (
    len(st.session_state.messages) != 0
    and st.session_state.messages[-1]["role"] == "user"
):
    agent.debug = devmode
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][user_date.weekday()]
    input_dict = {
        "use_current_location": use_current_location,
        "user_question": st.session_state.messages[-1]["content"],
        "weekday": weekday,
        "hour": user_time.hour,
    }
    if use_current_location:
        input_dict.update({"latitude": latitude, "longitude": longitude})

    # Generate and display assistant response
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
            except Exception:
                pass

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
