import os
import json
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# 1. .env 파일 로드
load_dotenv()

# 2. Scope 설정
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 3. 환경 변수 읽기
json_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
sheet_name = os.getenv("GOOGLE_SHEET_NAME")

if not json_str:
    print("오류: GOOGLE_SERVICE_ACCOUNT_JSON 환경 변수를 찾을 수 없습니다.")
    exit()

if not sheet_name:
    print("오류: GOOGLE_SHEET_NAME 환경 변수를 찾을 수 없습니다.")
    exit()

try:
    # 4. JSON 파싱 및 인증 객체 생성
    creds_info = json.loads(json_str)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
    
    # 5. gspread 클라이언트 승인 및 시트 접속
    client = gspread.authorize(creds)
    ss = client.open(sheet_name)
    
    # 6. 결과 출력
    print("연결 성공! 현재 존재하는 시트 목록:")
    for ws in ss.worksheets():
        print(f"- {ws.title}")

except Exception as e:
    print(f"오류 발생: {e}")