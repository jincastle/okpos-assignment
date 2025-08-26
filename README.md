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



### 상품 목록 조회
```bash
curl http://localhost:8000/shop/product/
```



### 방법 2: 다중 컨테이너 (docker-compose)

## 라이선스

이 프로젝트는 면접 과제용으로 제작되었습니다.

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.