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

# Streamlit 실행을 위해 추가된 부분
import streamlit as st
from streamlit_ui import main as streamlit_main

if __name__ == "__main__":
    # Streamlit 앱 실행
    streamlit_main()