import io
from PIL import Image
import pytest
from unittest.mock import MagicMock
import mlflow

@pytest.fixture(autouse=True)
def mock_mlflow_for_api(monkeypatch):
    """API 테스트 중 발생하는 외부 MLflow 서버 통신을 차단합니다."""
    mock_model = MagicMock()
    mock_model.predict.return_value = ["style_a"]
    
    monkeypatch.setattr("mlflow.sklearn.load_model", lambda uri: mock_model)
    monkeypatch.setattr("mlflow.tracking.MlflowClient", lambda: MagicMock())

def test_index_page(client):
    """메인 페이지가 정상적으로 로드되는지 확인"""
    response = client.get('/')
    assert response.status_code == 200

def test_process_non_image_file(client):
    """이미지가 아닌 텍스트 파일을 업로드했을 때 400 에러를 반환하는지 확인"""
    data = {
        'image': (io.BytesIO(b"this is a dummy text file"), 'test.txt'),
        'filter_type': 'grayscale'
    }
    response = client.post('/process', data=data, content_type='multipart/form-data')
    assert response.status_code == 400

def test_process_no_image_part(client):
    """폼 데이터에 'image' 키 자체가 누락된 채로 전송되었을 때 400 에러 확인"""
    # image 파일 없이 filter_type만 보냄
    data = {'filter_type': 'grayscale'}
    response = client.post('/process', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400

def test_process_empty_filename(client):
    """파일을 선택하지 않고 전송 버튼을 눌렀을 때 (빈 파일명) 400 에러 확인"""
    data = {
        # 파일 내용은 비어있고, 파일명도 '' 인 상태
        'image': (io.BytesIO(b""), ''), 
        'filter_type': 'grayscale'
    }
    response = client.post('/process', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400

def test_process_get_method_not_allowed(client):
    """POST 전용인 /process 라우트에 GET 요청을 보냈을 때 405 에러 확인"""
    response = client.get('/process')
    assert response.status_code == 405

def test_process_invalid_filter_type(client):
    """존재하지 않는 이상한 필터 이름을 보냈을 때 서버가 뻗지 않고 대응하는지 확인"""
    
    # 1. PIL을 이용해 1x1 픽셀짜리 정상적인 임시 이미지를 메모리상에 생성
    img = Image.new('RGB', (1, 1), color='black')
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    valid_png_bytes = img_io.getvalue()
    
    # 2. 방금 만든 진짜 이미지 데이터를 전송
    data = {
        'image': (io.BytesIO(valid_png_bytes), 'test.png'),
        'filter_type': 'weird_unknown_filter' # 이상한 필터값
    }
    response = client.post('/process', data=data, content_type='multipart/form-data')
    
    # processor.py 구현에 따라 200(기본 필터 적용) 또는 400(에러)인지 맞춰서 assert 작동 (500 에러로 뻗으면 안 됨)
    assert response.status_code == 400

def test_process_valid_image_with_ml_headers(client):
    """정상적인 이미지를 전송했을 때 200 반환 및 ML 예측 결과 헤더가 포함되는지 확인"""
    # 1. 테스트용 정상 이미지 생성
    img = Image.new('RGB', (10, 10), color='white')
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    valid_png_bytes = img_io.getvalue()
    
    # 2. 정상 필터(grayscale)로 데이터 전송
    data = {
        'image': (io.BytesIO(valid_png_bytes), 'test.png'),
        'filter_type': 'grayscale'
    }
    response = client.post('/process', data=data, content_type='multipart/form-data')
    
    # 3. 검증: 정상 처리(200) 및 이미지 반환 확인
    assert response.status_code == 200
    assert response.mimetype == 'image/png'
    
    # 4. 검증: MLOps 추론 결과 헤더가 존재하는지 확인
    assert 'X-ML-Prediction' in response.headers
    assert 'X-ML-Score' in response.headers

def test_process_crash_filter(client):
    """의도적 장애(crash) 필터를 전송했을 때 500 에러가 발생하는지 확인 (이슈 생성 트리거용)"""
    img = Image.new('RGB', (1, 1), color='black')
    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    
    data = {
        'image': (io.BytesIO(img_io.getvalue()), 'test.png'),
        'filter_type': 'crash'
    }
    response = client.post('/process', data=data, content_type='multipart/form-data')
    
    # crash 입력 시 서버에서 의도적으로 RuntimeError를 발생시키고 500을 반환해야 함
    assert response.status_code == 500