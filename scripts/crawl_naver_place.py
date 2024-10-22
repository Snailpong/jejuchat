import pandas as pd
from tqdm import tqdm

from utils.naver import extract_place_name

tqdm.pandas()

df = pd.read_csv("data/JEJU_PROCESSED.csv", encoding="cp949")
df = df.drop_duplicates(subset=["MCT_NM", "OP_YMD_x"], keep="first")
df["NAVER_PLACE_URL"] = (df["ADDR"] + " " + df["MCT_NM"]).progress_map(
    extract_place_name
)

df.to_csv("place.csv", index=False)
