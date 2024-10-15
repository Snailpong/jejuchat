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