from flask import Flask, render_template, request, send_file
import io
from app.processor import apply_image_filter 
from PIL import Image, UnidentifiedImageError

# app 폴더를 기준으로 상위 폴더의 templates를 바라보게 설정
app = Flask(__name__, template_folder='../templates')

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

    valid_filters = ['grayscale', 'edge', 'blur']
    
    # 2. 목록에 없는 필터면 바로 400 에러 반환
    if filter_type not in valid_filters:
        return "지원하지 않는 필터 타입", 400
    
    try:
        # 정상적인 이미지면 여기서 처리됨
        img = Image.open(file.stream)
        processed_img = apply_image_filter(img, filter_type)
        
        img_io = io.BytesIO()
        processed_img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
    
    except UnidentifiedImageError:
        # 이미지가 아닌 파일(텍스트 파일 등)이 들어와서 에러가 나면 400을 반환
        return "유효한 이미지 파일이 아닙니다", 400
    
