from lab_recommendation_prompt import lab_recommendation_prompt
import openai
from langchain_openai import AzureChatOpenAI


def lab_recommendation(user_input: str, topk_lab: list[dict]) -> list[dict]:
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
        result_list.append(result)

        print(result)
    
    return result_list
