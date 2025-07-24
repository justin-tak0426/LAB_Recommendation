from get_user_input import get_user_input
from find_topk import find_topk
from load_retriever import load_retriever
from get_docs import get_docs
import pandas as pd
from lab_recommendation import lab_recommendation
from get_result_list import final_prompts_output

# 환경 변수 로드
from dotenv import load_dotenv

load_dotenv()
# csv파일의 경로
doc_path = "./data/lab_data.xlsx"

# 데이터 입력받아옴
lab_total_info_df = pd.read_excel(doc_path, engine='openpyxl')
lab_search_docs = get_docs(lab_total_info_df)

# user에게 input을 받음 (top k, user query)
top_k = input("Enter the number of top results to retrieve (default is 3): ")
if not top_k.isdigit():
    top_k = 3
user_query = get_user_input()

# 검색 모델 로드
search_model = load_retriever(lab_search_docs, k=int(top_k) if top_k.isdigit() else 3)

# 데이터베이스에서 top k 결과 찾기
retrieved_docs = find_topk(search_model, user_query, top_k=int(top_k) if top_k.isdigit() else 3)

# top k documents에 대해 추천 이유 LLM을 통해 생성 또는 웹크롤링 진행
recommend_reason = lab_recommendation(top_k, user_query, retrieved_docs)

# 추천 결과 출력
final_result = []

# 웹에서 검색했을 시
try:
    if recommend_reason['index']==-1:
        print(recommend_reason['recommendation_reason'])

# 데이터베이스에서 검색했을 시
except:
    final_result = final_prompts_output(recommend_reason, lab_total_info_df)
    for result in final_result:
        print(result)

