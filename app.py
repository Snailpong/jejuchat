import os
from datetime import datetime

import streamlit as st

from agent import Agent
from utils.codes import STATE_CODE_DICT

if "agent" not in st.session_state:
    if api_key := os.getenv("GOOGLE_API_KEY"):
        pass
    else:
        from utils.api_key import google_ai_studio_api_key  # type: ignore

        api_key = google_ai_studio_api_key

    st.session_state.agent = Agent(api_key=api_key)

agent = st.session_state.agent

# Streamlit App UI

st.set_page_config(page_title="🍊참신한 제주 맛집!")

# Replicate Credentials
with st.sidebar:
    with st.expander("현재 정보 활용 설정", expanded=True):
        use_current_location_time = st.checkbox("현재 정보 활용")
        latitude = st.number_input("위도", format="%.6f", value=33.558277)
        longitude = st.number_input("경도", format="%.6f", value=126.75978)

        user_date = st.date_input("오늘 날짜", value=datetime.now())
        user_time = st.time_input("현재 시간", value=datetime.now())
    devmode = st.checkbox("dev 모드 (SQL쿼리 출력)")

st.title("혼저 옵서예!👋")
st.subheader("군맛난 제주 밥집🧑‍🍳 추천해드릴게예")
st.write(
    "#흑돼지 #갈치조림 #옥돔구이 #고사리해장국 #전복뚝배기 #한치물회 #빙떡 #오메기떡..🤤"
)

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "어드런 식당 찾으시쿠과?"}
    ]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


def clear_chat_history():
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
        "user_question": prompt,
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
