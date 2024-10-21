app_question_list = [
    "오늘 흑돼지 먹을만한 곳 추천해줘.",
    "내일 점심에 갈만한 고기국수 집 있어?",
    "제주시에서 현지인들이 많이 가는 식당 알려줘.",
    "커피 마실 수 있는 카페 추천해줘.",
    "가족끼리 갈만한 해물요리 식당은?",
    "비 오는 날 가기 좋은 식당 추천해줘.",
    "어린이와 함께 가기 좋은 식당 있어?",
    "지금 가면 사람이 많지 않은 식당 추천해줘.",
    "채식 가능한 식당 알려줘.",
    "제주에서 가장 오래된 전통식당은 어디야?",
]

ex_question_list = [
    {
        "question": "제주시 한림읍에 있는 카페 중 30대 이용 비중이 가장 높은 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '제주시' AND ADDR_2 = '한림읍' AND MCT_TYPE = '카페' ORDER BY RC_M12_AGE_30_CUS_CNT_RAT DESC LIMIT 1;",
    },
    {
        "question": "제주시 노형동에 있는 단품요리 전문점 중 이용건수가 상위 10%에 속하고 현지인 이용 비중이 가장 높은 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE WHERE ADDR_1 = '제주시' AND ADDR_2 = '노형동' AND MCT_TYPE = '단품요리 전문점' AND UE_CNT_GRP_NUM = 1 ORDER BY LOCAL_UE_CNT_RAT DESC LIMIT 1;",
    },
]
