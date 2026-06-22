import pandas as pd
import mlflow.sklearn
from app.config import MLFLOW_TRACKING_URI, MODEL_URI

def test_model_load_and_predict():
    """MLflow에서 챔피언 모델을 불러와 가상 데이터로 예측이 성공하는지 검증"""
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    try:
        model = mlflow.sklearn.load_model(MODEL_URI)
    except Exception as e:
        assert False, f"MLflow 모델 로드 실패: {e}\n(먼저 train.py를 실행해서 모델을 등록했는지 확인해!)"

    # numpy 대신 pandas를 사용하여 학습 데이터와 형태를 동일하게 맞춤
    dummy_features = pd.DataFrame(
        [[128.0, 64.0, 32.0]],
        columns=["brightness", "contrast", "edge_density"]
    )
    
    try:
        prediction = model.predict(dummy_features)
        
        assert len(prediction) == 1
        assert prediction[0] in ["Bright", "Dark", "Edgy"], f"예상치 못한 라벨 반환: {prediction[0]}"
    except Exception as e:
        assert False, f"모델 추론 중 에러 발생: {e}"