

valid_question_list = [
    {
        "question": "제주시 한림읍에 있는 카페 중 최근 12개월 동안 50대 이용 비중이 가장 높은 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '제주시' AND ADDR_2 = '한림읍' AND MCT_TYPE IN ('커피', '차') ORDER BY RC_M12_AGE_50_CUS_CNT_RAT DESC LIMIT 1;",
    },
    {
        "question": "서귀포시 성산읍에 있는 일식 전문점 중 18시부터 22시 사이에 이용 비중이 가장 높은 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '서귀포시' AND ADDR_2 = '성산읍' AND MCT_TYPE = '일식' ORDER BY HR_18_22_UE_CNT_RAT DESC LIMIT 1;",
    },
    {
        "question": "제주시 애월읍에 있는 분식 전문점 중 상위 25%에 속하는 이용건수를 기록한 곳들은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '제주시' AND ADDR_2 = '애월읍' AND MCT_TYPE = '분식' AND UE_CNT_GRP_NUM <= 2;",
    },
    {
        "question": "서귀포시 표선면 표선리에 있는 패밀리 레스토랑 중 최근 12개월 동안 20대 이하 이용 비중이 가장 높은 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '서귀포시' AND ADDR_2 = '표선면' AND ADDR_3 = '표선리' AND MCT_TYPE = '패밀리 레스토랑' ORDER BY RC_M12_AGE_UND_20_CUS_CNT_RAT DESC LIMIT 1;",
    },
    {
        "question": "제주시 연동에 위치한 맥주/요리주점 중 금요일 이용건수가 가장 많은 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '제주시' AND ADDR_2 = '연동' AND MCT_TYPE = '맥주/요리주점' ORDER BY FRI_UE_CNT_RAT DESC LIMIT 1;",
    },
    {
        "question": "서귀포시에 있는 뷔페 중 상위 25% 이내의 건당 평균 이용금액을 기록한 곳들은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '서귀포시' AND MCT_TYPE = '부페' AND UE_AMT_PER_TRSN_GRP_NUM <= 2;",
    },
    {
        "question": "제주시 노형동에 있는 피자 가게 중 현지인 이용 비중이 가장 높은 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '제주시' AND ADDR_2 = '노형동' AND MCT_TYPE = '피자' ORDER BY LOCAL_UE_CNT_RAT DESC LIMIT 1;",
    },
    {
        "question": "서귀포시 대정읍에 위치한 스테이크 전문점 중 최근 12개월 동안 남성 이용 비중이 가장 높은 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '서귀포시' AND ADDR_2 = '대정읍' AND MCT_TYPE = '스테이크' ORDER BY RC_M12_MAL_CUS_CNT_RAT DESC LIMIT 1;",
    },
    {
        "question": "제주시 용담삼동에 있는 아이스크림/빙수 가게 중 최근 12개월 동안 30대 이용 비중이 가장 높은 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '제주시' AND ADDR_2 = '용담삼동' AND MCT_TYPE = '아이스크림/빙수' ORDER BY RC_M12_AGE_30_CUS_CNT_RAT DESC LIMIT 1;",
    },
    {
        "question": "서귀포시 중문동에 위치한 꼬치구이 전문점 중 이용금액이 상위 50% 이상인 곳은?",
        "query": "SELECT * FROM JEJU_MCT_DATA WHERE ADDR_1 = '서귀포시' AND ADDR_2 = '중문동' AND MCT_TYPE = '꼬치구이' AND UE_AMT_GRP_NUM >= 4 LIMIT 1;",
    },
]
