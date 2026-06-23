import io
import logging
import traceback
import numpy as np
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageFilter, UnidentifiedImageError

from app.processor import apply_image_filter 
from app.issue import create_github_issue
from app.model_loader import load_champion_model  # 분리된 모듈 임포트

# === 추가된 부분: 설정값과 이슈 상태 업데이트 함수 임포트 ===
from app.config import LOW_CONFIDENCE_THRESHOLD
from app.retrain_issue import update_issue_state
# ============================================================

# 1) 로그 포맷: 시간 + 레벨 + 메시지
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d (%(funcName)s) | %(message)s"
)
logger = logging.getLogger("style_classifier")

app = Flask(__name__, template_folder='../templates')

# 앱 시작 시 모델 단 1회 로드
ml_model = load_champion_model()

def extract_features(img):
    gray_img = img.convert('L')
    img_arr = np.array(gray_img)
    brightness = np.mean(img_arr)
    contrast = np.std(img_arr)
    edge_img = gray_img.filter(ImageFilter.FIND_EDGES)
    edge_density = np.mean(np.array(edge_img))
    return np.array([[brightness, contrast, edge_density]])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return "이미지가 없습니다", 400
    
    file = request.files['image']
    if file.filename == '':
        return "파일이 선택되지 않았습니다", 400

    filter_type = request.form.get('filter_type', 'grayscale')

    # (A) 요청 들어온 것 자체를 기록
    logger.info(f"CALL /process | filter_type='{filter_type}' | filename='{file.filename}'")

    try:
        # 의도적 에러 삽입 테스트
        if filter_type == 'crash':
            raise RuntimeError("의도적 장애 추가")

        valid_filters = ['grayscale', 'edge', 'blur']
        if filter_type not in valid_filters:
            return "지원하지 않는 필터 타입", 400
        
        raw_img = Image.open(file.stream)
        prediction_result = "모델 미로드"
        confidence = 0.0
        
        # 모델 예측
        if ml_model is not None:
            features = extract_features(raw_img)
            pred = ml_model.predict(features)[0]
            proba = ml_model.predict_proba(features)[0]
            prediction_result = f"{pred}"
            confidence = float(max(proba))

            # === 추가된 부분: 예측 직후 모델 확신도 체크 및 이슈 생성 로직 ===
            # extract_features가 반환한 2차원 배열에서 값을 꺼내어 딕셔너리로 매핑합니다.
            input_features = {
                "brightness": float(features[0][0]),
                "contrast": float(features[0][1]),
                "edge_density": float(features[0][2])
            }
            update_issue_state(input_features, prediction_result, confidence, LOW_CONFIDENCE_THRESHOLD)
            # =================================================================

        processed_img = apply_image_filter(raw_img, filter_type)
        
        img_io = io.BytesIO()
        processed_img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # (B) 정상 처리 결과도 짧게 기록
        logger.info(f"OK /process | prediction={prediction_result} score={confidence:.4f}")
        
        response = send_file(img_io, mimetype='image/png')
        response.headers['X-ML-Prediction'] = str(prediction_result)
        response.headers['X-ML-Score'] = f"{confidence:.4f}"
        
        return response
    
    except UnidentifiedImageError:
        logger.warning("유효하지 않은 이미지 파일 업로드됨")
        return "유효한 이미지 파일이 아닙니다", 400
        
    except Exception as e:
        # (C) 디버깅 핵심: 에러 종류/메시지 + 스택트레이스 기록
        logger.exception(f"FAIL /process | error={type(e).__name__}: {e}")
        
        # (D) GitHub Issue 자동 생성 (크래시 발생 시)
        tb = traceback.format_exc()
        title = f"[Prod Error] /process failed: {type(e).__name__}"
        body = (
            f"## Summary\n* endpoint: /process\n* filter_type: {filter_type}\n\n"
            f"## Exception\n* type: {type(e).__name__}\n* message: {str(e)}\n\n"
            f"## Traceback\n```text\n{tb}\n```"
        )
        create_github_issue(title, body, logger)
        
        # (D) 사용자 응답은 심플하게 처리
        return "Internal Server Error", 500