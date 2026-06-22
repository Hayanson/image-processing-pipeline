import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import mlflow
import mlflow.sklearn

# 1. 분할되어 고정된 학습/테스트 데이터셋 로드
train_df = pd.read_csv("data/train_data.csv")
test_df = pd.read_csv("data/test_data.csv")

X_train = train_df[["brightness", "contrast", "edge_density"]]
y_train = train_df["style"]

X_test = test_df[["brightness", "contrast", "edge_density"]]
y_test = test_df["style"]

# 2. MLflow 설정
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("image-style-classification")

# 3. 모델 정의
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)

# 4. MLflow 로깅
with mlflow.start_run():
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 5)

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    mlflow.log_metric("test_accuracy", acc)
    
    # 두 원본 데이터를 모두 아티팩트로 기록
    mlflow.log_artifact("data/train_data.csv", artifact_path="data")
    mlflow.log_artifact("data/test_data.csv", artifact_path="data")

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="style-model"
    )

    print(f"모델 학습 및 MLflow 등록 완료! 테스트 정확도: {acc:.4f}")