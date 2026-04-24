from flask import Flask, render_template, request, send_file
import io
from app.processor import apply_image_filter 

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
    filter_type = request.form.get('filter_type', 'grayscale')
    
    from PIL import Image
    img = Image.open(file.stream)
    processed_img = apply_image_filter(img, filter_type)
    
    img_io = io.BytesIO()
    processed_img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')