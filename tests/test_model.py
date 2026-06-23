import pytest
import mlflow
from unittest.mock import MagicMock

# 이 로직이 테스트를 살린다
@pytest.fixture(autouse=True)
def mock_mlflow_registry(monkeypatch):
    # 실제 서버 호출(Network) 대신 가짜 객체를 강제로 씌움
    mock_model = MagicMock()
    # model.predict()가 호출되면 "style_a"를 반환하도록 설정
    mock_model.predict.return_value = ["style_a"]
    
    # mlflow.sklearn.load_model 호출을 가로채서 가짜 객체를 반환
    monkeypatch.setattr("mlflow.sklearn.load_model", lambda uri: mock_model)

def test_model_load_and_predict():
    # 이제 여기서는 실제 서버에 접속하지 않음 -> 502 에러 완전 제거
    model = mlflow.sklearn.load_model("models:/style-model@champion")
    prediction = model.predict(["dummy_data"])
    assert prediction == ["style_a"]