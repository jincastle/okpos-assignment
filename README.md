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


