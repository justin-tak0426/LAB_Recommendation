import streamlit as st
import os
import sys
from typing import Dict, List, Any
import pandas as pd

# Streamlit 페이지 설정
st.set_page_config(
    page_title="연구실 추천 시스템",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .result-container {
        background-color: #ffffff;
        border: 2px solid #e3f2fd;
        border-left: 6px solid #2c5aa0;
        border-radius: 15px;
        padding: 30px;
        margin: 30px 0;
        box-shadow: 0 6px 20px rgba(44, 90, 160, 0.12);
        transition: all 0.3s ease;
        position: relative;
        isolation: isolate;
    }
    .result-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(44, 90, 160, 0.2);
        border-color: #2c5aa0;
    }
    .result-container:not(:last-child) {
        margin-bottom: 40px;
    }
    .result-header {
        color: #2c5aa0;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 20px;
        padding: 12px 20px;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 8px;
        text-align: center;
        border: 1px solid #2c5aa0;
    }
    .result-content {
        color: #333;
        line-height: 1.8;
        font-size: 1rem;
        background-color: #fafafa;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #f0f0f0;
    }
    .stButton > button {
        background-color: #2c5aa0;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #1e3d6f;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    /* 셀렉트박스 스타일링 */
    .stSelectbox > div > div {
        background-color: #2c5aa0;
        color: white;
        border-radius: 5px;
    }
    .stSelectbox label {
        color: #2c5aa0;
        font-weight: bold;
    }
    
    /* 다크 모드 스타일 */
    @media (prefers-color-scheme: dark) {
        .main-header {
            color: #64b5f6;
        }
        .result-container {
            background-color: #2d2d2d;
            border: 2px solid #424242;
            border-left: 6px solid #64b5f6;
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            box-shadow: 0 6px 20px rgba(100, 181, 246, 0.12);
            position: relative;
            isolation: isolate;
        }
        .result-container:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(100, 181, 246, 0.2);
            border-color: #64b5f6;
        }
        .result-container:not(:last-child) {
            margin-bottom: 40px;
        }
        .result-header {
            color: #64b5f6;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid #64b5f6;
        }
        .result-content {
            color: #e0e0e0;
            background-color: #1e1e1e;
            border: 1px solid #424242;
        }
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """세션 상태 초기화"""
    if 'k_value' not in st.session_state:
        st.session_state.k_value = 3
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'user_query' not in st.session_state:
        st.session_state.user_query = ""


def render_result(result: str, index: int):
    """개별 결과 렌더링"""
    # HTML 태그를 포함한 텍스트를 안전하게 처리
    import html
    
    # HTML 태그 제거 및 이스케이프
    clean_result = html.escape(result).replace('\n', '<br>')
    
    st.markdown(f"""
    <div class="result-container">
        <div class="result-header">🏆 추천 #{index + 1}</div>
        <div class="result-content">
            {clean_result}
        </div>
    </div>
    """, unsafe_allow_html=True)

def run_lab_recommendation(user_query: str, k: int, status_callback=None):
    """연구실 추천 실행 함수"""
    from get_docs import get_docs
    from load_retriever import load_retriever
    from find_topk import find_topk
    from lab_recommendation import lab_recommendation
    from get_result_list import final_prompts_output
    
    # 데이터 로드
    doc_path = "./data/lab_info.xlsx"
    lab_total_info_df = pd.read_excel(doc_path, engine='openpyxl')
    lab_search_docs = get_docs(lab_total_info_df)
    
    # 검색 모델 로드 및 검색 실행
    search_model = load_retriever(lab_search_docs, k=k)
    retrieved_docs = find_topk(search_model, user_query, top_k=k)
    
    # 추천 이유 생성 (상태 콜백과 함께)
    recommend_reason = lab_recommendation(k, user_query, retrieved_docs, status_callback=status_callback)
    
    # 최종 결과 생성
    final_result = []
    
    # 웹 검색 결과인지 확인 (리스트이고 첫 번째 항목의 index가 -1)
    if isinstance(recommend_reason, list) and len(recommend_reason) > 0 and recommend_reason[0].get('index') == -1:
        # 웹 검색 결과를 final_prompts_output 형태로 변환
        web_results = []
        for item in recommend_reason:
            web_results.append(item.get('recommendation_reason', '추천 결과를 찾을 수 없습니다.'))
        return web_results, True  # (결과, 웹검색여부)
    
    try:
        # 일반적인 연구실 추천 결과인 경우
        final_result = final_prompts_output(recommend_reason, lab_total_info_df)
    except Exception as e:
        # 오류 발생 시 기본 메시지 반환
        final_result = [f"추천 결과 생성 중 오류가 발생했습니다: {str(e)}"]
    
    return final_result, False  # (결과, 웹검색여부)

def main():
    """Streamlit 메인 앱"""
    # 세션 상태 초기화
    init_session_state()
    
    # 헤더
    st.markdown('<h1 class="main-header">🔬 연구실 추천 시스템</h1>', unsafe_allow_html=True)
    
    # 사용자 입력과 K값 선택을 같은 섹션에
    st.markdown("### 💭 어떤 연구 분야에 관심이 있으신가요?")
    
    # 입력창과 K값 선택을 나란히 배치
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_query = st.text_area(
            "연구 관심사를 자유롭게 입력해주세요",
            placeholder="예: 인공지능과 머신러닝을 활용한 의료 연구에 관심있습니다.",
            height=100,
            key="user_input"
        )
    
    with col2:
        st.markdown("**추천 개수**")
        k_value = st.selectbox(
            "개수 선택",
            options=[1, 2, 3, 4, 5],
            index=2,  # 기본값 3
            key="k_selector",
            label_visibility="collapsed"
        )
        st.session_state.k_value = k_value
        st.markdown(f"**{k_value}개 추천**")
    
    # 검색 버튼
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 연구실 추천받기", use_container_width=True):
            if user_query.strip():
                st.session_state.user_query = user_query
                
                # 초기 검색 스피너
                search_placeholder = st.empty()
                with search_placeholder.container():
                    with st.spinner(f'🔄 {st.session_state.k_value}개의 연구실을 찾고 있습니다...'):
                        try:
                            # 상태 표시를 위한 placeholder 생성
                            status_placeholder = st.empty()
                            
                            # 상태 콜백 함수 정의
                            def show_status(message):
                                status_placeholder.info(message)
                            
                            # 연구실 추천 실행 (상태 콜백 포함)
                            results, is_web_search = run_lab_recommendation(user_query, st.session_state.k_value, show_status)
                            
                            # 결과 검증
                            if results is None:
                                st.error("❌ 추천 결과가 None입니다.")
                                return
                            elif not isinstance(results, list):
                                st.error(f"❌ 예상치 못한 결과 타입: {type(results)}")
                                return
                            elif len(results) == 0:
                                st.warning("⚠️ 추천 결과가 없습니다.")
                                return
                            
                            # 웹 검색 결과인 경우 메시지 표시 (정확한 플래그 사용)
                            if is_web_search:
                                st.info("🌐 데이터베이스에 적합한 연구실이 없어 웹에서 추가 검색을 진행했습니다.")
                            
                            # 상태 placeholder 정리
                            status_placeholder.empty()
                            
                            st.session_state.search_results = results
                            st.success(f"✅ {len(results)}개의 연구실을 추천해드립니다!")
                            
                        except Exception as e:
                            import traceback
                            error_details = traceback.format_exc()
                            st.error(f"❌ 오류가 발생했습니다: {str(e)}")
                            st.error(f"상세 오류 정보: {error_details}")
                            print(f"Streamlit Error: {error_details}")
            else:
                st.warning("⚠️ 연구 관심사를 입력해주세요.")
    
    # 결과 표시
    if st.session_state.search_results:
        st.markdown("---")
        st.markdown("## 📋 추천 결과")
        st.markdown(f"**'{st.session_state.user_query}'**에 대한 추천 연구실입니다.")
        
        # 각 결과를 개별 컨테이너로 분리
        for i, result in enumerate(st.session_state.search_results):
            with st.container():
                render_result(result, i)
                # 마지막 항목이 아니면 구분선 추가
                if i < len(st.session_state.search_results) - 1:
                    st.markdown("<br>", unsafe_allow_html=True)
    
    # 사이드바 정보
    with st.sidebar:
        st.markdown("### 📚 사용 가이드")
        st.info("""
        1. **연구 관심사 입력**: 관심있는 연구 분야나 주제를 자유롭게 입력하세요.
        
        2. **추천 개수 선택**: 1~5개 중에서 원하는 추천 개수를 선택하세요.
        
        3. **검색 실행**: '연구실 추천받기' 버튼을 클릭하면 AI가 가장 적합한 연구실을 추천해드립니다.
        """)
        
        st.markdown("### 🎯 추천 시스템 특징")
        st.success("""
        - AI 기반 맞춤형 추천
        - 연구 분야 매칭
        - 상세한 추천 이유 제공
        """)

if __name__ == "__main__":
    main()