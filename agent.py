import os

import faiss
import google.generativeai as genai  # Gemini 설정
import numpy as np
import pandas as pd
import torch
from transformers import AutoModel, AutoTokenizer

# 경로 설정
module_path = "./modules"

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

# Gemini 모델 선택
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat()
# 경로 설정
data_path = "./data"


# import shutil
# os.makedirs("/root/.streamlit", exist_ok=True)
# shutil.copy("secrets.toml", "/root/.streamlit/secrets.toml")


# CSV 파일 로드
## 자체 전처리를 거친 데이터 파일 활용
csv_file_path = "JEJU_MCT_DATA_modified.csv"
df = pd.read_csv(os.path.join(data_path, csv_file_path))

# 최신연월 데이터만 가져옴
df = df[df["기준연월"] == df["기준연월"].max()].reset_index(drop=True)

# 디바이스 설정
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

# Hugging Face의 사전 학습된 임베딩 모델과 토크나이저 로드
model_name = "jhgan/ko-sroberta-multitask"
tokenizer = AutoTokenizer.from_pretrained(model_name)
embedding_model = AutoModel.from_pretrained(model_name).to(device)

print(f"Device is {device}.")


# FAISS 인덱스 로드 함수
def load_faiss_index(index_path=os.path.join(module_path, "faiss_index.index")):
    """
    FAISS 인덱스를 파일에서 로드합니다.

    Parameters:
    index_path (str): 인덱스 파일 경로.

    Returns:
    faiss.Index: 로드된 FAISS 인덱스 객체.
    """
    if os.path.exists(index_path):
        # 인덱스 파일에서 로드
        index = faiss.read_index(index_path)
        print(f"FAISS 인덱스가 {index_path}에서 로드되었습니다.")
        return index
    else:
        raise FileNotFoundError(f"{index_path} 파일이 존재하지 않습니다.")


# 텍스트 임베딩
def embed_text(text):
    # 토크나이저의 출력도 GPU로 이동
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(
        device
    )
    with torch.no_grad():
        # 모델의 출력을 GPU에서 연산하고, 필요한 부분을 가져옴
        embeddings = embedding_model(**inputs).last_hidden_state.mean(dim=1)
    return embeddings.squeeze().cpu().numpy()  # 결과를 CPU로 이동하고 numpy 배열로 변환


# 임베딩 로드
embeddings = np.load(os.path.join(module_path, "embeddings_array_file.npy"))


# RAG

# FAISS 인덱스를 파일에서 로드
index_path = os.path.join(module_path, "faiss_index.index")
index = load_faiss_index(index_path)


def generate_response_with_faiss(
    question: str,
    time,
    local_choice,
    max_count=10,
    k=3,
    print_prompt=True,
) -> str:
    filtered_df = df

    # 검색 쿼리 임베딩 생성
    query_embedding = embed_text(question).reshape(1, -1)

    # 가장 유사한 텍스트 검색 (3배수)
    distances, indices = index.search(query_embedding, k * 3)

    # FAISS로 검색된 상위 k개의 데이터프레임 추출
    filtered_df = filtered_df.iloc[indices[0, :]].copy().reset_index(drop=True)

    filtered_df = filtered_df.reset_index(drop=True).head(k)

    # 선택된 결과가 없으면 처리
    if filtered_df.empty:
        return "질문과 일치하는 가게가 없습니다."

    # 참고할 정보와 프롬프트 구성
    reference_info = "\n".join(filtered_df["text"].to_list())

    # 응답을 받아오기 위한 프롬프트 생성
    prompt = f"질문: {question} 특히 {local_choice}을 선호해\n참고할 정보:\n{reference_info}\n응답:"

    if print_prompt:
        print("-----------------------------" * 3)
        print(prompt)
        print("-----------------------------" * 3)

    # 응답 생성
    response = chat.send_message(prompt)

    return response.text
