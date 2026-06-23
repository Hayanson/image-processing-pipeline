import sys
import io
import pytest
from unittest.mock import MagicMock
import mlflow
import gspread

# 이제 파이썬이 루트 폴더를 인식하므로 정상적으로 import 됨
from app.app import app 

@pytest.fixture
def client():
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
    # 1. Flask가 파일로 인식할 수 있도록 io.BytesIO 필수 사용
    dummy_image = (io.BytesIO(b"dummy_bytes"), "test.jpg")
    
    # 2. API 호출 시 multipart/form-data 선언
    response = client.post(
        "/process",
        data={"file": dummy_image},
        content_type="multipart/form-data",
        headers={"X-ML-Header": "test_value"}
    )
    
    # 3. 에러 발생 시 로그 출력
    if response.status_code != 200:
        pytest.fail(f"API 에러 발생! 상태 코드: {response.status_code}, 상세 로그: {response.data.decode('utf-8')}")
        
    assert response.status_code == 200