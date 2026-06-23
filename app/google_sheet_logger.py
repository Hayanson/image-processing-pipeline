import os
import json
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

_sheet_client = None
_spreadsheet = None

def get_spreadsheet():
    global _sheet_client, _spreadsheet
    if _spreadsheet is not None:
        return _spreadsheet
    
    sheet_name = os.getenv("GOOGLE_SHEET_NAME")
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    
    if not sheet_name or not service_account_json:
        raise RuntimeError("구글 시트 환경 변수나 JSON 키가 설정되지 않았습니다.")
    
    # JSON 텍스트를 파이썬 딕셔너리로 변환하여 인증
    credentials_info = json.loads(service_account_json)
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPE)
    
    _sheet_client = gspread.authorize(credentials)
    _spreadsheet = _sheet_client.open(sheet_name)
    return _spreadsheet

def append_prediction_log(filename: str, prediction: str, score: float, serving_model: str):
    try:
        worksheet = get_spreadsheet().worksheet("prediction_logs")
        worksheet.append_row([
            datetime.now().isoformat(timespec="seconds"),
            filename,
            prediction,
            round(float(score), 4),
            serving_model
        ])
    except Exception as e:
        import logging
        logging.getLogger("style_classifier").error(f"Prediction Log Error: {e}")

def append_feedback_log(filename: str, prediction: str, correct_label: str, score: float, serving_model: str):
    worksheet = get_spreadsheet().worksheet("feedback_logs")
    worksheet.append_row([
        datetime.now().isoformat(timespec="seconds"),
        filename,
        prediction,
        correct_label,
        round(float(score), 4),
        serving_model
    ])