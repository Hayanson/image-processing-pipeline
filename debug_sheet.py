import os
import json
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# 1. .env 파일 로드
load_dotenv()

# 2. 접근 권한(Scope) 설정
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 3. 환경 변수 읽기
json_str = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

if not json_str:
    print("오류: GOOGLE_SERVICE_ACCOUNT_JSON 환경 변수를 찾을 수 없습니다.")
    exit()

# 4. 스프레드시트 고유 ID 직접 입력
# 구글 시트 주소창 URL 중 /d/ 와 /edit 사이에 있는 문자열을 넣으세요.
SPREADSHEET_ID = "1lgK_MyiMJUE7V1TrlGbZS1FIe454VjSE7efZ5Ce5j3A"

try:
    # 5. JSON 파싱 및 인증 객체 생성
    creds_info = json.loads(json_str)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPE)
    
    # 6. gspread 클라이언트 승인 및 시트 접속 (ID로 접근)
    client = gspread.authorize(creds)
    ss = client.open_by_key(SPREADSHEET_ID)
    
    # 7. 결과 출력
    print("연결 성공! 현재 존재하는 시트 목록:")
    for ws in ss.worksheets():
        print(f"- {ws.title}")

except Exception as e:
    print(f"오류 발생: {e}")
    try:
        print(f"상세 에러 메시지: {e.response.text}")
    except:
        pass