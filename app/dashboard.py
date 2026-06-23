import os
import json
import gspread
import pandas as pd
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# 1. 환경 변수 로드 (절대 경로 사용)
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

# 2. Scope 및 환경 변수 설정
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

# 3. 스프레드시트 고유 ID (성공했던 디버그 코드에서 가져온 ID를 입력하세요)
SPREADSHEET_ID = "1lgK_MyiMJUE7V1TrlGbZS1FIe454VjSE7efZ5Ce5j3A"

@st.cache_resource
def get_spreadsheet():
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        st.error("오류: GOOGLE_SERVICE_ACCOUNT_JSON 환경 변수가 없습니다.")
        return None
    try:
        creds_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
        client = gspread.authorize(creds)
        
        # 이름 대신 고유 ID로 시트 접근
        return client.open_by_key(SPREADSHEET_ID)
    except Exception as e:
        st.error(f"구글 시트 연결 실패: {e}")
        return None

def load_sheet(sheet_name: str) -> pd.DataFrame:
    ss = get_spreadsheet()
    if not ss: return pd.DataFrame()
    try:
        ws = ss.worksheet(sheet_name)
        all_values = ws.get_all_values()
        
        if len(all_values) <= 1: 
            return pd.DataFrame()
            
        # 첫 번째 행을 컬럼명으로 지정
        return pd.DataFrame(all_values[1:], columns=all_values[0])
    except Exception:
        return pd.DataFrame()

# 대시보드 UI 설정
st.set_page_config(page_title="MLOps Dashboard", layout="wide")
st.title("이미지 스타일 분류 모니터링 대시보드")

# 데이터 로드
pred_df = load_sheet("prediction_logs")
feedback_df = load_sheet("feedback_logs")

# 1. 운영 지표
st.subheader("운영 지표")
if not pred_df.empty:
    pred_df["score"] = pd.to_numeric(pred_df["score"], errors="coerce")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Requests", len(pred_df))
    col2.metric("Average Confidence", round(pred_df["score"].mean(), 4))
    col3.metric("Low Confidence", len(pred_df[pred_df["score"] < 0.65]))
    
    canary_requests = len(pred_df[pred_df["serving_model"] == "challenger"]) if "serving_model" in pred_df.columns else 0
    col4.metric("Canary Requests", canary_requests)

    st.line_chart(pred_df["score"])
    st.dataframe(pred_df.tail(10), use_container_width=True)
else:
    st.info("예측 로그 데이터가 없습니다.")

# 2. 사용자 피드백
st.subheader("사용자 피드백")
if not feedback_df.empty:
    if "prediction" in feedback_df.columns and "correct_label" in feedback_df.columns:
        wrong_df = feedback_df[feedback_df["prediction"] != feedback_df["correct_label"]]
        col5, col6, col7 = st.columns(3)
        col5.metric("Feedback Count", len(feedback_df))
        col6.metric("Wrong Prediction", len(wrong_df))
        col7.metric("Wrong Rate", f"{(len(wrong_df)/len(feedback_df)):.2%}")
        
    st.dataframe(feedback_df.tail(10), use_container_width=True)
else:
    st.info("피드백 데이터가 없습니다.")