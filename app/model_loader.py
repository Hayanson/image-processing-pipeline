import logging
import mlflow.sklearn
from app.config import MLFLOW_TRACKING_URI, MODEL_URI

logger = logging.getLogger("style_classifier")

def load_champion_model():
    """MLflow에서 챔피언 모델을 불러오는 전용 함수"""
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    try:
        model = mlflow.sklearn.load_model(MODEL_URI)
        logger.info("MLflow 챔피언 모델 로드 성공")
        return model
    except Exception as e:
        logger.error(f"모델 로드 실패: {e}")
        return None