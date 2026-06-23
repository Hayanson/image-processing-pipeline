import os
import json
from pathlib import Path
import gspread
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

@st.cache_resource
def get_spreadsheet():
    credentials_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPE)
    client = gspread.authorize(credentials)
    return client.open(GOOGLE_SHEET_NAME)

def load_sheet(sheet_name: str) -> pd.DataFrame:
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

st.set_page_config(page_title="MLOps Dashboard", layout="wide")
st.title("이미지 스타일 분류 모니터링 대시보드")

if not GOOGLE_SHEET_NAME or not GOOGLE_SERVICE_ACCOUNT_JSON:
    st.error("구글 시트 환경 변수나 JSON 키가 설정되지 않았습니다.")
    st.stop()

try:
    pred_df = load_sheet("prediction_logs")
    feedback_df = load_sheet("feedback_logs")
except Exception as e:
    st.error(f"데이터 로드 실패: {e}")
    st.stop()

st.subheader("운영 지표")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Requests", len(pred_df))

if len(pred_df) > 0:
    pred_df["score"] = pd.to_numeric(pred_df["score"], errors="coerce")
    col2.metric("Average Confidence", round(pred_df["score"].mean(), 4))
    col3.metric("Low Confidence", len(pred_df[pred_df["score"] < 0.65]))
    
    canary_count = len(pred_df[pred_df["serving_model"] == "challenger"]) if "serving_model" in pred_df.columns else 0
    col4.metric("Canary Requests", canary_count)

    st.subheader("Confidence Trend")
    st.line_chart(pred_df.reset_index(), x="index", y="score")
    
    st.subheader("최근 예측 기록")
    st.dataframe(pred_df.tail(10), use_container_width=True)
else:
    st.info("아직 예측 로그가 없습니다.")

st.subheader("사용자 피드백")
if len(feedback_df) > 0:
    wrong_df = feedback_df[feedback_df["prediction"] != feedback_df["correct_label"]]
    col5, col6, col7 = st.columns(3)
    col5.metric("Feedback Count", len(feedback_df))
    col6.metric("Wrong Prediction Feedback", len(wrong_df))
    
    wrong_rate = len(wrong_df) / len(feedback_df)
    col7.metric("Wrong Feedback Rate", f"{wrong_rate:.2%}")
    
    st.subheader("최근 피드백 기록")
    st.dataframe(feedback_df.tail(10), use_container_width=True)
else:
    st.info("아직 피드백이 없습니다.")