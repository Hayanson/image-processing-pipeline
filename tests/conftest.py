import sys
from pathlib import Path
import pytest

# 프로젝트 최상위 경로를 강제로 시스템 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client