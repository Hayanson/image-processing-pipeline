import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import mlflow
import mlflow.sklearn
from mlflow.client import MlflowClient

# 1. 데이터 경로 설정 및 로드
TRAIN_DATA_PATH = "ml/data/train_data.csv"
TEST_DATA_PATH = "ml/data/test_data.csv"

train_df = pd.read_csv(TRAIN_DATA_PATH)
test_df = pd.read_csv(TEST_DATA_PATH)

# 특성(X)과 정답(y) 분리 (정답 컬럼명이 'label'인 경우)
X_train = train_df.drop("style", axis=1)
y_train = train_df["style"]
X_test = test_df.drop("style", axis=1)
y_test = test_df["style"]

# 2. 학습할 모델 딕셔너리 정의 (에러가 났던 부분)
models = {
    "RandomForest": RandomForestClassifier(random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42)
}

# 3. 최고 성능 모델 추적을 위한 변수 초기화
best_acc = 0.0
best_model_version = None

# 4. 모델 학습 및 MLflow 기록 반복문
for model_name, model in models.items():
    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model_type", model_name)

        # 모델 학습 및 예측
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)

        # 평가 지표 기록
        mlflow.log_metric("test_accuracy", acc)
        
        # 데이터 파일 아티팩트로 기록
        mlflow.log_artifact(TRAIN_DATA_PATH, artifact_path="data")
        mlflow.log_artifact(TEST_DATA_PATH, artifact_path="data")

        # 모델 등록
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="style-model"
        )
        
        # 최고 성능 갱신 시 챔피언 후보 기록
        if acc > best_acc:
            best_acc = acc
            best_model_version = model_info.registered_model_version
            
        print(f"[{model_name}] 모델 학습 완료! 정확도: {acc:.4f}")

# 5. 반복문 종료 후 최고 성능 버전에만 'champion' 별칭 지정
client = MlflowClient()
client.set_registered_model_alias(
    name="style-model",
    alias="champion",
    version=best_model_version
)

print(f"최종 챔피언 지정 완료! (버전: {best_model_version}, 정확도: {best_acc:.4f})")