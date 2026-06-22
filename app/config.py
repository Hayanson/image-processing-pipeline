import os

# MLflow Tracking DB 위치 (기본값은 로컬 sqlite)
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")

# MLflow 실험 및 모델 이름 설정
EXPERIMENT_NAME = "image-style-classification"
MODEL_NAME = "style-model"
MODEL_ALIAS = "champion"

# 모델을 불러올 때 사용할 고정 URI
MODEL_URI = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"