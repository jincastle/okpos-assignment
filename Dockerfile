# Python 3.8 이미지 사용
FROM python:3.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# 가상환경 생성 및 활성화
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# 가상환경에서 Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# Django 마이그레이션 및 서버 실행
CMD ["sh", "-c", "python manage.py makemigrations shop && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
