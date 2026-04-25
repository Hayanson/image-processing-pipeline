from app.app import app

if __name__ == '__main__':
    # 디버그 모드는 로컬에서만 켜고, 배포 환경에서는 끌 수 있게 세팅
    app.run(host='0.0.0.0', port=5000, debug=True)