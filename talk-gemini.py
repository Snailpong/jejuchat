import os

import google.generativeai as genai

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

chat = model.start_chat()


def speak(text):
    response = chat.send_message(text)
    return response.text


while (prompt := input("You: ")) != "":
    print("Bot:", speak(prompt))
