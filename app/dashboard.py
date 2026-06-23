# app/dashboard.py 수정본
import os
import json
import gspread
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# 1. 루트 경로의 .env 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# ... (SCOPE 및 GOOGLE_... 변수 설정 부분은 동일) ...

@st.cache_resource
def get_spreadsheet():
    try:
        credentials_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPE)
        client = gspread.authorize(credentials)
        return client.open(GOOGLE_SHEET_NAME)
    except Exception as e:
        st.error(f"구글 시트 연결 실패: {e}")
        return None

def load_sheet(sheet_name: str) -> pd.DataFrame:
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return pd.DataFrame() # 빈 데이터프레임 반환
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        records = worksheet.get_all_records()
        return pd.DataFrame(records)
    except gspread.exceptions.WorksheetNotFound:
        st.warning(f"시트 '{sheet_name}'을 찾을 수 없습니다.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

# 대시보드 로직...
pred_df = load_sheet("prediction_logs")
feedback_df = load_sheet("feedback_logs")

# 만약 데이터가 없으면 안내 문구만 띄우고 아래 로직 건너뜀
if pred_df.empty:
    st.info("데이터가 없습니다. 로그가 쌓일 때까지 기다려주세요.")
else:
    # (기존의 col1, col2... 메트릭 계산 로직들)
    # 이제 여기서 로직이 돌아도 멈추지 않아!