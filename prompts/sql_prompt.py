sql_generation_prompt = """
Context for SQL Generation:
You are tasked with converting natural language queries into SQL queries. The SQL queries will operate on a table called JEJU_MCT_DATA that contains data about businesses in Jeju from January 2023 to December 2023. The columns include metrics about customer usage, business type, location, and time-based behaviors. The queries may involve filtering businesses based on geographical location, customer age group, business type, and various other attributes. Below is the schema of the table JEJU_MCT_DATA:

Table Schema (JEJU_MCT_DATA)
- YM: STRING, year-month format of the data (e.g., "20230105" for January 5, 2023).

- MCT_NM: STRING, name of the business.

- OP_YMD: STRING, opening date of the business.

- MCT_TYPE: STRING, type of the business, must be one of the following 30 food-related categories:
  ['가정식', '단품요리 전문', '커피', '베이커리', '일식', '치킨', '중식', '분식', '햄버거',
   '양식', '맥주/요리주점', '아이스크림/빙수', '피자', '샌드위치/토스트', '차', '꼬치구이',
   '기타세계요리', '구내식당/푸드코트', '떡/한과', '도시락', '도너츠', '주스', '동남아/인도음식',
   '패밀리 레스토랑', '기사식당', '야식', '스테이크', '포장마차', '부페', '민속주점']
  - In cases where the business type might be ambiguous (e.g., "카페" can refer to both "커피" and "차"), the SQL filter should allow for multiple possible values for MCT_TYPE.

- ADDR: STRING, address of the business.

- ADDR_1: STRING, the primary city category, representing "제주시" or "서귀포시".
- ADDR_2: STRING, the secondary location category, representing neighborhood, town, or township ("~~동", "~~읍", "~~면").
- ADDR_3: STRING, the tertiary location category, representing village or hamlet ("~~리") and used only when ADDR_2 is an "읍" or "면".
  
  When constructing SQL queries, use the following guidelines for the ADDR fields:
  - For "제주시 한림읍", the query should include `ADDR_1 = '제주시' AND ADDR_2 = '한림읍'`.
  - For "서귀포시 표선면 표선리", the query should include `ADDR_1 = '서귀포시' AND ADDR_2 = '표선면' AND ADDR_3 = '표선리'`.
  - For broad queries like "제주시", use only `ADDR_1 = '제주시'`.
  - For a general query covering all locations in "제주도" or "제주특별자치도", omit the ADDR fields to include all records.

- UE_CNT_GRP_NUM: INTEGER, usage count percentile group as a number based on the total usage count in six percentile bands:
  * 1 = "상위 10% 이하"
  * 2 = "10~25%"
  * 3 = "25~50%"
  * 4 = "50~75%"
  * 5 = "75~90%"
  * 6 = "90% 초과"

  When a query asks for "상위 25% 이내," the condition should be `NUM <= 2` to capture both the 10% 이하 and 10~25% ranges.
  Similarly, if the query asks for "상위 50% 이상," the condition should be `NUM >= 4` to capture the 50~75%, 75~90%, and 90% 초과 ranges.

- UE_AMT_GRP_NUM: INTEGER, spending percentile group as a number based on the total spending in six percentile bands:
  * 1 = "상위 10% 이하"
  * 2 = "10~25%"
  * 3 = "25~50%"
  * 4 = "50~75%"
  * 5 = "75~90%"
  * 6 = "90% 초과"
  
  Apply similar logic when querying for spending percentiles.

- UE_AMT_PER_TRSN_GRP_NUM: INTEGER, average spending per transaction group as a number based on the total average spending in six percentile bands:
  * 1 = "상위 10% 이하"
  * 2 = "10~25%"
  * 3 = "25~50%"
  * 4 = "50~75%"
  * 5 = "75~90%"
  * 6 = "90% 초과"
  
  The same conditions apply here: use `NUM <= X` for percentile ranges below the specified value and `NUM >= X` for percentile ranges above the specified value.

- MON_UE_CNT_RAT, TUE_UE_CNT_RAT, ..., SUN_UE_CNT_RAT: FLOAT, daily usage rate percentages (e.g., Monday usage rate).

- HR_5_11_UE_CNT_RAT, ..., HR_23_4_UE_CNT_RAT: FLOAT, time-slot usage rates (e.g., 5am-11am, 12pm-1pm).

- RC_M12_MAL_CUS_CNT_RAT, RC_M12_FME_CUS_CNT_RAT: These columns represent the percentage of male and female customers over the last 12 months, respectively.
  - RC_M12_MAL_CUS_CNT_RAT: Percentage of male customers.
  - RC_M12_FME_CUS_CNT_RAT: Percentage of female customers.
  
  Use these columns to filter businesses based on the gender distribution of their customers. For example, use RC_M12_MAL_CUS_CNT_RAT to find businesses with a high percentage of male customers, or RC_M12_FME_CUS_CNT_RAT for businesses with a high percentage of female customers.

- RC_M12_AGE_UND_20_CUS_CNT_RAT, RC_M12_AGE_30_CUS_CNT_RAT, RC_M12_AGE_40_CUS_CNT_RAT, RC_M12_AGE_50_CUS_CNT_RAT, RC_M12_AGE_OVR_60_CUS_CNT_RAT: These columns represent the percentage of customers in different age groups over the last 12 months.
  - RC_M12_AGE_UND_20_CUS_CNT_RAT: Percentage of customers under 20 years old.
  - RC_M12_AGE_30_CUS_CNT_RAT: Percentage of customers in their 30s.
  - RC_M12_AGE_40_CUS_CNT_RAT: Percentage of customers in their 40s.
  - RC_M12_AGE_50_CUS_CNT_RAT: Percentage of customers in their 50s.
  - RC_M12_AGE_OVR_60_CUS_CNT_RAT: Percentage of customers over 60 years old.

  Use these columns to filter businesses based on the age distribution of their customers. For example, use RC_M12_AGE_30_CUS_CNT_RAT to find businesses with a high percentage of customers in their 30s, or RC_M12_AGE_OVR_60_CUS_CNT_RAT for businesses frequented by customers over 60.

Instructions:
- Input: A natural language query that asks for specific filtering criteria based on the columns described above.
- Output: An SQL query that accurately reflects the given query's constraints.
When referring to locations, assume location data is stored in the ADDR column and must be filtered by matching a substring (e.g., "제주시 한림읍" should match records where the ADDR column contains "한림읍").
Usage count, spending, and other statistical groupings are already categorized, so use the appropriate percentile bands for filtering (UE_CNT_GRP, UE_AMT_GRP, UE_AMT_PER_TRSN_GRP).
Use ORDER BY to rank the results where applicable, such as "highest percentage" or "most frequent use."

Examples:
- Example 1:
Input (Natural Language): "제주시 한림읍에 있는 카페 중 30대 이용 비중이 가장 높은 곳은?"
Output (SQL Query in Json Format):
{
"query": "SELECT * 
FROM JEJU_MCT_DATA 
WHERE ADDR_1 = '제주시' 
  AND ADDR_2 = '한림읍' 
  AND MCT_TYPE IN ('커피', '차') 
ORDER BY RC_M12_AGE_30_CUS_CNT_RAT DESC 
LIMIT 1;"
}


- Example 2:
Input (Natural Language): "제주시 노형동에 있는 단품요리 전문점 중 이용건수가 상위 10%에 속하고 현지인 이용 비중이 가장 높은 곳은?"
Output (SQL Query in Json Format):
{
"query": "SELECT * 
FROM JEJU_MCT_DATA 
WHERE ADDR_1 = '제주시' 
  AND ADDR_2 = '노형동' 
  AND MCT_TYPE = '단품요리 전문점' 
  AND UE_CNT_GRP_NUM = 1 
ORDER BY LOCAL_UE_CNT_RAT DESC
LIMIT 1;"
}

- Example 3:
Input (Natural Language): "제주시에서 50대 이용 비중이 가장 높은 햄버거 가게는?"
Output (SQL Query in Json Format):
{
"query": "SELECT * 
FROM JEJU_MCT_DATA 
WHERE ADDR_1 = '제주시' 
  AND MCT_TYPE = '햄버거' 
ORDER BY RC_M12_AGE_50_CUS_CNT_RAT DESC 
LIMIT 1;"
}

"""