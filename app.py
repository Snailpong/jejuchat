from datetime import datetime

import streamlit as st
from streamlit_geolocation import streamlit_geolocation

# Streamlit App UI

st.set_page_config(page_title="🍊참신한 제주 맛집!")

# Replicate Credentials
with st.sidebar:
    st.title("🍊참신한! 제주 맛집")

    st.write("")

    st.subheader("언드레 가신디가?")

    # selectbox 레이블 공백 제거
    st.markdown(
        """
        <style>
        .stSelectbox label {  /* This targets the label element for selectbox */
            display: none;  /* Hides the label element */
        }
        .stSelectbox div[role='combobox'] {
            margin-top: -20px; /* Adjusts the margin if needed */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    time = st.sidebar.selectbox("", ["아침", "점심", "오후", "저녁", "밤"], key="time")

    st.write("")

    st.subheader("어드레가 맘에 드신디가?")

    # radio 레이블 공백 제거
    st.markdown(
        """
        <style>
        .stRadio > label {
            display: none;
        }
        .stRadio > div {
            margin-top: -20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    local_choice = st.radio("", ("제주도민 맛집", "관광객 맛집"))

    # Group location-related inputs into an expandable box
    with st.expander("Location Settings", expanded=True):
        use_current_location = st.checkbox("현재 정보 활용")
        location = streamlit_geolocation()
        latitude = st.number_input("위도", format="%.6f", value=location["latitude"])
        longitude = st.number_input("경도", format="%.6f", value=location["longitude"])

        st.time_input("현재 시간", value=datetime.now())
        weekdays = [
            "월요일",
            "화요일",
            "수요일",
            "목요일",
            "금요일",
            "토요일",
            "일요일",
        ]
        selected_weekday = st.selectbox(
            "요일 선택", weekdays, index=datetime.now().weekday()
        )

    devmode = st.checkbox("dev 모드 (SQL쿼리 출력)")

st.title("혼저 옵서예!👋")
st.subheader("군맛난 제주 밥집🧑‍🍳 추천해드릴게예")

st.write("")

st.write(
    "#흑돼지 #갈치조림 #옥돔구이 #고사리해장국 #전복뚝배기 #한치물회 #빙떡 #오메기떡..🤤"
)

st.write("")

image_path = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTHBMuNn2EZw3PzOHnLjDg_psyp-egZXcclWbiASta57PBiKwzpW5itBNms9VFU8UwEMQ&usqp=CAU"
image_html = f"""
<div style="display: flex; justify-content: center;">
    <img src="{image_path}" alt="centered image" width="50%">
</div>
"""
st.markdown(image_html, unsafe_allow_html=True)

st.write("")

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
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Pass latitude and longitude to the response generator
            response = "Nothing"
            st.markdown(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
