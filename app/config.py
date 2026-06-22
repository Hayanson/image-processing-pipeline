
# MLflow Tracking DB 위치 (기본값은 로컬 sqlite)
import os

# ngrok을 켜면 아래 주소를 "https://xxx.ngrok-free.dev" 형태로 바꿔주세요.
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_URL", "sqlite:///mlflow.db")

EXPERIMENT_NAME = "image-style-classification"
MODEL_NAME = "style-model"
MODEL_ALIAS = "champion"
MODEL_URI = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
