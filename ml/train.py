import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import mlflow
import mlflow.sklearn
from mlflow.client import MlflowClient

# ... (상단 설정 및 데이터 로드 부분은 기존과 동일) ...

# 최고 성능을 추적할 변수 준비
best_acc = 0.0
best_model_version = None

for model_name, model in models.items():
    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model_type", model_name)

        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)

        mlflow.log_metric("test_accuracy", acc)
        
        mlflow.log_artifact(TRAIN_DATA_PATH, artifact_path="data")
        mlflow.log_artifact(TEST_DATA_PATH, artifact_path="data")

        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name="style-model"
        )
        
        # 현재 모델의 정확도가 기존 최고 정확도보다 높으면 챔피언 후보 갱신
        if acc > best_acc:
            best_acc = acc
            best_model_version = model_info.registered_model_version
            
        print(f"[{model_name}] 모델 학습 완료! 정확도: {acc:.4f}")

# 반복문이 모두 끝나고 나면, 가장 성능이 좋았던 버전에만 champion 부여
client = MlflowClient()
client.set_registered_model_alias(
    name="style-model",
    alias="champion",
    version=best_model_version
)

print(f"최종 챔피언 지정 완료! (버전: {best_model_version}, 정확도: {best_acc:.4f})")