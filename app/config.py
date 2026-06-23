
# MLflow Tracking DB 위치 (기본값은 로컬 sqlite)
import os


MLFLOW_TRACKING_URI = "https://imposing-retaining-widow.ngrok-free.dev"

EXPERIMENT_NAME = "image-style-classification"
MODEL_NAME = "style-model"
MODEL_ALIAS = "champion"
MODEL_URI = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
