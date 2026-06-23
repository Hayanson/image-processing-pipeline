import os

# 시스템 환경 변수에서 MLFLOW_URL 값을 찾고, 없으면 ngrok 주소 사용
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_URL", "https://imposing-retaining-widow.ngrok-free.dev")

# drift / retrain issue report를 위한 임곗값 설정
LOW_CONFIDENCE_THRESHOLD = 0.65

# === 카나리 배포 설정 ===
CANARY_ENABLED = True
CANARY_RATIO = 0.25  # 25%의 트래픽을 신규 모델(challenger)로 전송

MODEL_NAME = "style-model"

CHAMPION_MODEL_URI = f"models:/{MODEL_NAME}@champion"
CHALLENGER_MODEL_URI = f"models:/{MODEL_NAME}@challenger"
MODEL_URI = CHAMPION_MODEL_URI