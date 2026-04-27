# 파이썬 3.9 가벼운 버전(slim)을 베이스 이미지로 사용
FROM python:3.9-slim

# 컨테이너 내부의 작업 폴더를 /app으로 설정
WORKDIR /app

# 필요한 라이브러리 목록 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 코드 전체를 컨테이너 안으로 복사
COPY . .

# Flask 환경 변수 설정
ENV FLASK_APP=app/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 5000번 포트 열기
EXPOSE 5000

# 도커 컨테이너가 켜질 때 실행할 명령어
# 기존 코드: CMD ["flask", "run"]
# 변경 후:
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app.app:app"]