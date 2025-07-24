import pandas as pd
from typing import List, Dict
import openai
from langchain_openai import AzureChatOpenAI


def get_final_prompt_list(recommendation_list: List[Dict], df: pd.DataFrame) -> List[str]:
    """
    추천 결과와 연구실 데이터프레임을 받아 연구실별 출력 메시지 리스트 생성
    """
    messages = []
    if len(recommendation_list) == 0:
        print("Warning: No recommendations found.")
        return messages
   
    for idx, r in enumerate(recommendation_list, start=1):
        
        df1 = df[df['index'].astype(int) == int(r['index'])]

        # 데이터가 없으면 스킵
        if df1.empty:
            print(f"Warning: No data found for index {r['index']}")
            continue

        # 각 열 값 추출
        name = df1['professor_name']
        research_institute = df1['research_institute']
        department = df1['department']
        degree = df1['degree']
        professor_title = df1['professor_title']
        lab_name = df1['lab_name']
        lab_website = df1['lab_website']
        research_keywords = df1['research_keywords']
        professor_career = df1['professoer_career']
        telephone = df1['telephone']
        fax = df1['fax']
        email = df1['email']
        research_topics = df1['research_topics']
        research_techniques = df1['research_techniques']
        lab_description = df1['lab_description']
        recent_publications = df1['recent_publications']
        reason = r['recommendation_reason']


        # 출력 메시지 생성
        prompt = f"""
  
        🔎 {idx}번째 추천 연구실 {reason}

        🎓 [연구실명] {lab_name}
        👨‍🏫 [지도교수] {professor_title} {name}
        🏛️ [소속기관] {research_institute} / {department}
        🎓 [학위 과정] {degree}


        🔬 [연구 분야 요약]
        • 핵심 키워드: {research_keywords}
        • 주요 주제: {research_topics}
        • 사용 기법: {research_techniques}


        📌 [추천 이유]
        해당 연구실을 추천하는 이유에 대해 설명한다.
        💡 [연구실 특징]
        {lab_description}


        🧑‍🔬 [교수 경력]
        {professor_career}

        📚 [최근 주요 논문]
        {recent_publications}

        📬 [연구실 접근 정보]
        • 홈페이지: {lab_website}
        • 이메일: {email}
        • 전화: {telephone} / 팩스: {fax}
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        messages.append(prompt)

    return messages


def final_prompts_output(recommendation_list: List[Dict], df: pd.DataFrame) -> str:
    
    messages = get_final_prompt_list(recommendation_list, df)
    final_result_list = []

    for idx, message in enumerate(messages, start=1):
        final_prompt = f"""
        ### 역할 ###
        당신은 대학원 진학을 희망하는 학생에게 연구실을 추천하는 조력자입니다.
        사용자의 질의(연구 관심 분야 또는 경험 기반 요청)와 유사도 분석 결과로 추천된 연구실 정보를 바탕으로,
        각 연구실에 대해 시각적으로 구분된 요약을 제공합니다.

        ### 입력 ###
        {message}

        ### 출력 지침 ###
        다음 항목을 포함하여 사용자에게 친절하고 신뢰감 있게 안내하시오:
        - 연구실명, 교수명, 소속
        - 연구 키워드와 주제, 사용 기술
        - 추천 이유 (사용자 조건과의 연관성 중심)
        - 연구실만의 특징, 교수 경력, 최근 논문 (이때 교수 학력, 경력, 논문은 원본 그대로 출력)
        - 논문 갯수는 최대 5개로 제한
        - 홈페이지 / 이메일 등 접근 수단

        시각적 구분을 위해 줄바꿈 및 기호(●, 🔬, 📈 등)를 활용하시오.
        과장 없이 핵심 정보를 요약하되, 정보 전달이 명확하도록 구성하시오.
        """

        # LLM에게 lab_info_prompt를 전달하여 추천 이유 생성
        model = AzureChatOpenAI(model='gpt-4o')
        response = model.invoke(final_prompt)
        response_text = response.content

        final_result_list.append(response_text)


    return final_result_list
