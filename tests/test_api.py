import io
from PIL import Image

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