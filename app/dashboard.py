import os
import json
import gspread
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

from pathlib import Path

# 현재 이 파일(dashboard.py)의 위치를 기준으로 프로젝트 루트를 찾음
# 구조: 프로젝트루트/app/dashboard.py -> 부모의 부모가 루트가 아님, 부모가 루트임.
# 네 구조가 project/app/dashboard.py 라면 부모 폴더(project/)를 가리켜야 함
BASE_DIR = Path(__file__).resolve().parent.parent 
env_path = BASE_DIR / '.env'

# .env 파일이 존재하는지 확인 (디버깅용)
if not env_path.exists():
    print(f"DEBUG: .env 파일을 찾을 수 없음: {env_path}")
else:
    load_dotenv(dotenv_path=env_path)

# 환경 변수 로드
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

# 환경 변수가 비어있는지 확인
if GOOGLE_SERVICE_ACCOUNT_JSON is None:
    raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON 환경 변수가 None입니다. .env 파일이나 환경 변수 설정을 다시 확인하세요.")

# 프로젝트 루트의 .env 경로 지정
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

@st.cache_resource
def get_spreadsheet():
    try:
        if not GOOGLE_SERVICE_ACCOUNT_JSON: return None
        creds_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
        return gspread.authorize(creds).open(GOOGLE_SHEET_NAME)
    except Exception as e:
        st.error(f"구글 시트 연결 실패: {e}")
        return None

def load_sheet(sheet_name: str) -> pd.DataFrame:
    ss = get_spreadsheet()
    if not ss: return pd.DataFrame()
    try:
        ws = ss.worksheet(sheet_name)
        all_values = ws.get_all_values()
        if len(all_values) <= 1: return pd.DataFrame()
        # 첫 번째 행을 헤더로, 나머지를 데이터로 강제 변환
        return pd.DataFrame(all_values[1:], columns=all_values[0])
    except Exception:
        return pd.DataFrame()

# 대시보드 UI 설정
st.set_page_config(page_title="MLOps Dashboard", layout="wide")
st.title("이미지 스타일 분류 모니터링 대시보드")

# 데이터 한 번만 로드
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
    col4.metric("Canary Requests", len(pred_df[pred_df["serving_model"] == "challenger"]) if "serving_model" in pred_df.columns else 0)

    st.line_chart(pred_df["score"])
    st.dataframe(pred_df.tail(10), use_container_width=True)
else:
    st.info("예측 로그 데이터가 없습니다.")

# 2. 사용자 피드백
st.subheader("사용자 피드백")
if not feedback_df.empty:
    wrong_df = feedback_df[feedback_df["prediction"] != feedback_df["correct_label"]]
    col5, col6, col7 = st.columns(3)
    col5.metric("Feedback Count", len(feedback_df))
    col6.metric("Wrong Prediction", len(wrong_df))
    col7.metric("Wrong Rate", f"{(len(wrong_df)/len(feedback_df)):.2%}")
    st.dataframe(feedback_df.tail(10), use_container_width=True)
else:
    st.info("피드백 데이터가 없습니다.")