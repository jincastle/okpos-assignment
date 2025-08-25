# OKPOS Assignment

## 🚀 한 번에 실행하기

```bash
# 1. Python 버전 확인
python --version

# 2. 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. Django 실행
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

# 5. 브라우저에서 확인
# http://127.0.0.1:8000/
```