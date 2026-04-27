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