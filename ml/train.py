import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import mlflow
import mlflow.sklearn

# config.py가 최상단에 있으므로 import
from app.config import MLFLOW_TRACKING_URI, EXPERIMENT_NAME

# 1. 오류 방지를 위한 절대 경로 설정 (PDF 3p 반영)
BASE_DIR = os.path.dirname(__file__) # 현재 폴더(ml)의 경로
DATA_DIR = os.path.join(BASE_DIR, "data")
TRAIN_DATA_PATH = os.path.join(DATA_DIR, "train_data.csv")
TEST_DATA_PATH = os.path.join(DATA_DIR, "test_data.csv")

train_df = pd.read_csv(TRAIN_DATA_PATH)
test_df = pd.read_csv(TEST_DATA_PATH)

X_train = train_df[["brightness", "contrast", "edge_density"]]
y_train = train_df["style"]
X_test = test_df[["brightness", "contrast", "edge_density"]]
y_test = test_df["style"]

# 2. MLflow 설정 (config.py에서 불러옴)
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

# 3. 비교할 여러 모델 정의 (PDF 8p 반영)
models = {
    "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=200)
}

# 4. 반복문을 돌며 각각의 모델을 학습하고 MLflow에 기록
for model_name, model in models.items():
    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model_type", model_name)

        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)

        mlflow.log_metric("test_accuracy", acc)
        
        mlflow.log_artifact(TRAIN_DATA_PATH, artifact_path="data")
        mlflow.log_artifact(TEST_DATA_PATH, artifact_path="data")

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="style-model"
        )
        print(f"[{model_name}] 모델 학습 및 MLflow 등록 완료! 정확도: {acc:.4f}")