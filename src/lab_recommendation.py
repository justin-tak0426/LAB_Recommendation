from lab_recommendation_prompt import lab_recommendation_prompt
import openai
from langchain_openai import AzureChatOpenAI
from search_agent import search_web


def lab_recommendation(k, user_input: str, topk_lab: list[dict]) -> list[dict]:
    result_list = []
    
    for lab in topk_lab:
        index = lab["index"]
        lab_info_prompt = lab_recommendation_prompt(user_input, lab["text"])


        # LLM에게 lab_info_prompt를 전달하여 추천 이유 생성
        model = AzureChatOpenAI(model='gpt-4o')
        response = model.invoke(lab_info_prompt)
        response_text = response.content

        result = {
            "index": index,
            "lab_info": lab["text"],
            "recommendation_reason": response_text
        }

        if "관련도 없음" in response_text:
            continue

        result_list.append(result)

    if len(result_list) == 0:
        print("\n\n\n\n추천할 연구실이 데이터 베이스 상에 없습니다.\n 웹에서 검색을 실시합니다.\n\n\n\n")
        result = search_web(user_input, max_results=k)

        return result

    
    return result_list
