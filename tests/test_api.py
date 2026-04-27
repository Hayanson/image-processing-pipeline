import io

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