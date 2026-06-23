import random
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from app.config import (
    MLFLOW_TRACKING_URI,
    CHAMPION_MODEL_URI,
    CHALLENGER_MODEL_URI,
    CANARY_ENABLED,
    CANARY_RATIO
)

_champion_model = None
_challenger_model = None
_model_info_cache = {}

def load_champion_model():
    global _champion_model
    if _champion_model is None:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        _champion_model = mlflow.sklearn.load_model(CHAMPION_MODEL_URI)
    return _champion_model

def load_challenger_model():
    global _challenger_model
    if _challenger_model is None:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        try:
            _challenger_model = mlflow.sklearn.load_model(CHALLENGER_MODEL_URI)
        except Exception:
            # 챌린저 모델이 아직 MLflow에 등록되지 않았을 경우를 대비한 예외 처리
            return None
    return _challenger_model

def select_serving_model():
    """설정된 비율(CANARY_RATIO)에 따라 챔피언 또는 챌린저 모델을 반환합니다."""
    if CANARY_ENABLED and random.random() < CANARY_RATIO:
        challenger = load_challenger_model()
        if challenger is not None:
            return challenger, "challenger"
    
    return load_champion_model(), "champion"

def get_model_info(serving_model_type):
    """현재 예측에 사용된 모델의 메타데이터(버전, 정확도 등)를 반환합니다."""
    if serving_model_type in _model_info_cache:
        return _model_info_cache[serving_model_type]

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    try:
        uri = CHAMPION_MODEL_URI if serving_model_type == "champion" else CHALLENGER_MODEL_URI
        info = mlflow.models.get_model_info(uri)
        run = MlflowClient().get_run(info.run_id)
        
        model_info = {
            "run_id": info.run_id,
            "model_type": run.data.params.get("model_type", "Unknown"),
            "test_accuracy": run.data.metrics.get("test_accuracy", "Unknown"),
        }
        _model_info_cache[serving_model_type] = model_info
        return model_info
    except Exception:
        return {
            "run_id": "unknown",
            "model_type": "Unknown",
            "test_accuracy": "Unknown"
        }