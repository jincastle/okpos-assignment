# OKPOS Assignment

## 실행 방법

### 로컬 환경
```bash
# 가상환경 생성
python -m venv venv
# 가상환경 활성화
source venv/bin/activate
# 의존성 패키지 설치
pip install -r requirements.txt
# 데이터베이스 마이그레이션
python manage.py migrate

# 테스트 데이터 설정 (선택사항)
python manage.py setup_test_data
# 개발 서버 실행
python manage.py runserver
```

### Docker
```bash
# Docker 이미지 빌드
docker build -t okpos-assignment .

# Docker 컨테이너 실행
docker run -p 8000:8000 okpos-assignment

# 백그라운드에서 실행하려면
docker run -d -p 8000:8000 okpos-assignment

# 컨테이너 중지
docker stop <container_id>

# 컨테이너 목록 확인
docker ps

# 컨테이너 로그 확인
docker logs <container_id>
```

## 접속 URL
- http://localhost:8000/

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


