import os
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv
from tavily import TavilyClient
from openai import OpenAI, AzureOpenAI

# .env 파일에서 환경변수 로드
load_dotenv()

# 환경변수 읽기
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_TYPE = os.getenv("OPENAI_API_TYPE", "openai")  # 기본값 설정
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")


# 전역 클라이언트 초기화
def _init_clients():
    """API 클라이언트들을 초기화합니다."""
    
    # Tavily 클라이언트 초기화
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    
    # OpenAI 클라이언트 초기화
    if OPENAI_API_TYPE == "azure":
        openai_client = AzureOpenAI(
            api_key=OPENAI_API_KEY,
            api_version=OPENAI_API_VERSION,
            azure_endpoint=AZURE_ENDPOINT
        )
        print(f"✅ Azure OpenAI 클라이언트 초기화 완료 (엔드포인트: {AZURE_ENDPOINT})")
    else:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI 클라이언트 초기화 완료")
    
    print("✅ Tavily 클라이언트 초기화 완료")
    return tavily_client, openai_client

# 전역 클라이언트
tavily_client, openai_client = _init_clients()

def search_web(query: str, max_results: int, status_callback=None) -> Dict[str, Any]:
    """
    웹검색 + GPT 분석을 수행하는 메인 함수
    
    입력 형식:
        1. 단일 쿼리: query="검색하고 싶은 내용"
        2. 옵션 설정: max_results=5 (검색 결과 수), include_score=True (점수 포함)
    
    Args:
        query (str): 검색할 질의
        max_results (int): 검색 결과 수 (1-10, 기본값: 5)
        include_score (bool): 점수 포함 여부 (기본값: False)
    
    Returns:
        Dict: {
            "query": 입력한 질의,
            "answer": GPT가 생성한 답변,
            "score": 답변 품질 점수 1-10 (include_score=True일 때만),
            "sources": 웹 검색 결과 리스트,
            "timestamp": 검색 시간,
            "model": 사용 모델명
        }
    
    사용 예시:
        # 기본 검색
        result = search_web("국내 AI 연구소")
        print(result["answer"])
        
        # 점수 포함 검색
        result = search_web("국내 AI 연구소", include_score=True)
        print(f"점수: {result['score']}/10")
        
        # 검색 결과 10개로 확장
        result = search_web("국내 AI 연구소", max_results=10)
    """
    try:
        # 1. Tavily로 웹 검색
        if status_callback:
            status_callback(f"🌐 '{query}' 웹 검색 중...")
        else:
            print(f"🌐 '{query}' 검색 중...")
            
        search_response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=True,
            include_raw_content=True
        )
        
        if status_callback:
            status_callback("✅ 웹 검색 완료")
        else:
            print("✅ 웹 검색 완료")

        # 검색 결과 처리
        sources = []
        if "results" in search_response:
            for item in search_response["results"]:
                sources.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "published_date": item.get("published_date", "")
                })
                
        # print(f"✅ {len(sources)}개 결과 찾음")
        
        if not sources:
            return 0
        
        # 2. GPT로 결과 분석
        if status_callback:
            status_callback("🤖 AI 분석 중...")
        else:
            print("🤖 GPT 분석 중...")
        
        # 컨텍스트 구성
        context = "웹 검색 결과:\n\n"
        for i, source in enumerate(sources, 1):
            context += f"[출처 {i}] {source['title']}\n"
            context += f"URL: {source['url']}\n"
            context += f"내용: {source['content']}\n\n"
        
        messages = [
            {
                "role": "system",
                "content": f"""
다음 원칙에 따라 답변해주세요:
1. 검색된 실제 정보를 바탕으로 사실적이고 정확한 답변 제공
2. 여러 출처의 정보를 종합하여 포괄적인 답변 작성
3. 구체적이고 실용적인 정보 포함
4. 출처 정보 적절히 언급하여 신뢰성 제고"""
            },
            {
                "role": "user",
                "content": f"""질문: {query}

{context}

위 검색 결과를 바탕으로 질문에 대한 정확하고 도움이 되는 답변을 작성해주세요."""
            }
        ]
        
        gpt_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        
        answer = gpt_response.choices[0].message.content
        
        
        
        if status_callback:
            status_callback("✅ 분석 완료")
        else:
            print("✅ 분석 완료")
        
        # k개로 분할하여 반환
        recommendations = []
        if max_results > 1:
            # GPT에게 k개로 나누어 달라고 요청
            split_prompt = f"다음 내용을 정확히 {max_results}개의 개별 추천으로 나누어 주세요. 각각을 '===추천1===', '===추천2===' 형식으로 구분해 주세요:\n\n{answer}"
            
            split_response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": split_prompt}],
                temperature=0.3,
                max_tokens=2048,
            )
            
            split_answer = split_response.choices[0].message.content
            parts = split_answer.split("===추천")
            
            for i in range(1, min(len(parts), max_results + 1)):
                part = parts[i]
                if part.startswith(str(i) + "==="):
                    content = part[len(str(i) + "==="):].strip()
                elif "===" in part:
                    content = part.split("===", 1)[1].strip()
                else:
                    content = part.strip()
                
                if content:
                    recommendations.append({
                        "index": -1,
                        "lab_info": content,
                        "recommendation_reason": content
                    })
        
        # 분할 실패하거나 k=1인 경우 원본 반환
        if len(recommendations) == 0:
            recommendations = [{
                "index": -1,
                "lab_info": answer,
                "recommendation_reason": answer
            }]
        
        # k개 맞추기
        while len(recommendations) < max_results:
            recommendations.append(recommendations[-1].copy())
            
        return recommendations[:max_results]
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        # 오류 시에도 k개 리스트 반환
        return [{"index": -1, "lab_info": f"검색 중 오류: {str(e)}", "recommendation_reason": f"검색 중 오류: {str(e)}"}] * max_results