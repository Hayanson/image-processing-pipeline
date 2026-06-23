import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import mlflow
import gspread

# 네 FastAPI 앱을 가져오는 경로 (앱 구조에 맞게 수정 필요)
from app.app import app 

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolate_external_dependencies(monkeypatch):
    """외부 인프라(MLflow, 구글 시트) 통신을 완벽히 차단하는 가짜(Mock) 객체 주입"""
    # 1. MLflow 통신 차단 (ngrok 502 에러 방지)
    mock_model = MagicMock()
    mock_model.predict.return_value = ["style_a"]
    monkeypatch.setattr("mlflow.sklearn.load_model", lambda uri: mock_model)
    monkeypatch.setattr("mlflow.tracking.MlflowClient", lambda: MagicMock())
    
    # 2. 구글 시트 통신 차단 (API 내부 500 에러 방지)
    mock_gspread_client = MagicMock()
    monkeypatch.setattr("gspread.authorize", lambda creds: mock_gspread_client)
    
    # 인증 객체 생성도 차단
    try:
        monkeypatch.setattr("google.oauth2.service_account.Credentials.from_service_account_info", lambda info, scopes=None: MagicMock())
    except Exception:
        pass

def test_process_valid_image_with_ml_headers():
    # 1. 테스트용 더미 파일
    dummy_image = b"dummy_bytes"
    
    # 2. API 호출 (경로와 파라미터는 기존 네 코드에 맞춰)
    response = client.post(
        "/process", # 실제 API 엔드포인트로 변경
        files={"file": ("test.jpg", dummy_image, "image/jpeg")},
        headers={"X-ML-Header": "test_value"} # 기존에 있던 헤더 설정
    )
    
    # 3. 500 에러 발생 시, 구체적인 원인을 터미널에 강제 출력
    if response.status_code == 500:
        pytest.fail(f"API 500 에러 발생! 상세 로그: {response.text}")
        
    assert response.status_code == 200