import pytest
from unittest.mock import MagicMock
import mlflow
import gspread

# 네 Flask 앱 가져오기
from app.app import app 

@pytest.fixture
def client():
    # Flask 내장 테스트 클라이언트 설정
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def isolate_external_dependencies(monkeypatch):
    """외부 인프라(MLflow, 구글 시트) 통신을 완벽히 차단하는 가짜(Mock) 객체 주입"""
    # 1. MLflow 통신 차단
    mock_model = MagicMock()
    mock_model.predict.return_value = ["style_a"]
    monkeypatch.setattr("mlflow.sklearn.load_model", lambda uri: mock_model)
    monkeypatch.setattr("mlflow.tracking.MlflowClient", lambda: MagicMock())
    
    # 2. 구글 시트 통신 차단
    mock_gspread_client = MagicMock()
    monkeypatch.setattr("gspread.authorize", lambda creds: mock_gspread_client)
    
    try:
        monkeypatch.setattr("google.oauth2.service_account.Credentials.from_service_account_info", lambda info, scopes=None: MagicMock())
    except Exception:
        pass

def test_process_valid_image_with_ml_headers(client):
    # 1. 테스트용 더미 파일 설정 (Flask 호환 방식)
    dummy_image = (b"dummy_bytes", "test.jpg")
    
    # 2. API 호출
    response = client.post(
        "/process",
        data={"file": dummy_image},
        headers={"X-ML-Header": "test_value"}
    )
    
    # 3. 500 에러 발생 시 로그 출력
    if response.status_code == 500:
        pytest.fail(f"API 500 에러 발생! 상세 로그: {response.data.decode('utf-8')}")
        
    assert response.status_code == 200