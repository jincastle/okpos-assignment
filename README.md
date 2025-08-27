# OKPOS Assignment

## 실행 방법

### 로컬 환경
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker
```bash
docker build -t okpos-assignment .
docker run -p 8000:8000 okpos-assignment
```

## 접속 URL
- http://localhost:8000/shop/product/

## TEST

### pytest 사용
```bash
# 전체 테스트 실행
python -m pytest

# 커버리지 측정과 함께 실행
python -m pytest --cov=shop --cov-report=term-missing

# HTML 커버리지 리포트 생성
python -m pytest --cov=shop --cov-report=html

# 테스트 수집 확인
python -m pytest --collect-only
```

### 테스트 커버리지 확인
```bash
# 터미널에서 커버리지 확인
python -m pytest --cov=shop --cov-report=term-missing

# HTML 리포트 생성 후 브라우저에서 확인
python -m pytest --cov=shop --cov-report=html
open htmlcov/index.html
```


