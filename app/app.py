import io
import logging
import traceback
import numpy as np
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageFilter, UnidentifiedImageError

from app.processor import apply_image_filter 
from app.issue import create_github_issue
from app.model_loader import select_serving_model, get_model_info 
from app.config import LOW_CONFIDENCE_THRESHOLD
from app.retrain_issue import update_issue_state

# === 추가된 부분: 구글 시트 로깅 함수 임포트 ===
from app.google_sheet_logger import append_prediction_log, append_feedback_log
from dotenv import load_dotenv
load_dotenv()
# ===============================================

# 1) 로그 포맷
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d (%(funcName)s) | %(message)s")
logger = logging.getLogger("style_classifier")

app = Flask(__name__, template_folder='../templates')

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
    logger.info(f"CALL /process | filter_type='{filter_type}' | filename='{file.filename}'")

    try:
        if filter_type == 'crash':
            raise RuntimeError("의도적 장애 추가")

        valid_filters = ['grayscale', 'edge', 'blur']
        if filter_type not in valid_filters:
            return "지원하지 않는 필터 타입", 400
        
        raw_img = Image.open(file.stream)
        prediction_result = "모델 미로드"
        confidence = 0.0
        
        ml_model, serving_model_type = select_serving_model()
        model_info = {}

        if ml_model is not None:
            features = extract_features(raw_img)
            pred = ml_model.predict(features)[0]
            proba = ml_model.predict_proba(features)[0]
            prediction_result = f"{pred}"
            confidence = float(max(proba))
            
            model_info = get_model_info(serving_model_type)

            input_features = {
                "brightness": float(features[0][0]),
                "contrast": float(features[0][1]),
                "edge_density": float(features[0][2])
            }
            update_issue_state(input_features, prediction_result, confidence, LOW_CONFIDENCE_THRESHOLD)
            
            # === 추가된 부분: 예측 로그를 구글 시트에 기록 ===
            append_prediction_log(file.filename, prediction_result, confidence, serving_model_type)
            # ===============================================

        processed_img = apply_image_filter(raw_img, filter_type)
        
        img_io = io.BytesIO()
        processed_img.save(img_io, 'PNG')
        img_io.seek(0)
        
        logger.info(f"OK /process | prediction={prediction_result} score={confidence:.4f} serving_model={serving_model_type}")
        
        response = send_file(img_io, mimetype='image/png')
        response.headers['X-ML-Prediction'] = str(prediction_result)
        response.headers['X-ML-Score'] = f"{confidence:.4f}"
        response.headers['X-ML-Serving-Model'] = serving_model_type
        response.headers['X-Filename'] = file.filename # 파일명 전달용 헤더 추가
        
        return response
    
    except UnidentifiedImageError:
        logger.warning("유효하지 않은 이미지 파일 업로드됨")
        return "유효한 이미지 파일이 아닙니다", 400
        
    except Exception as e:
        logger.exception(f"FAIL /process | error={type(e).__name__}: {e}")
        tb = traceback.format_exc()
        title = f"[Prod Error] /process failed: {type(e).__name__}"
        body = (f"## Summary\n* endpoint: /process\n* filter_type: {filter_type}\n\n"
                f"## Exception\n* type: {type(e).__name__}\n* message: {str(e)}\n\n"
                f"## Traceback\n```text\n{tb}\n```")
        create_github_issue(title, body, logger)
        return "Internal Server Error", 500

# === 추가된 부분: 사용자 피드백을 받는 엔드포인트 ===
@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    try:
        append_feedback_log(
            data.get('filename', 'unknown'),
            data.get('prediction', 'unknown'),
            data.get('correct_label', 'unknown'),
            float(data.get('score', 0.0)),
            data.get('serving_model', 'unknown')
        )
        logger.info(f"OK /feedback | correct_label={data.get('correct_label')}")
        return jsonify({"status": "feedback saved"})
    except Exception as e:
        logger.exception(f"FAIL /feedback | error={type(e).__name__}: {e}")
        return jsonify({"status": "feedback save failed"}), 500