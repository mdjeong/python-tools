# 베이스 이미지를 설정합니다. Python 3.11 버전의 경량화된(slim) 버전을 사용합니다.
FROM python:3.11-slim

# 컨테이너 내부에서 작업할 디렉토리를 '/app'으로 설정합니다.
# 이후의 명령어들은 이 디렉토리 안에서 실행됩니다.
WORKDIR /app

# 현재 폴더에 있는 dependency 리스트(requirements.txt)를 컨테이너의 작업 디렉토리로 복사합니다.
COPY requirements.txt .

# pip를 사용하여 requirements.txt에 명시된 라이브러리들을 설치합니다.
# --no-cache-dir 옵션은 캐시 데이터를 저장하지 않아 이미지 크기를 줄여줍니다.
RUN pip install --no-cache-dir -r requirements.txt

# 현재 폴더의 모든 파일(소스 코드 등)을 컨테이너의 작업 디렉토리(/app)로 복사합니다.
# .dockerignore에 등록된 파일들은 복사되지 않습니다.
COPY . .

# 컨테이너가 8000번 포트를 사용한다는 것을 명시합니다. (문서화 용도)
EXPOSE 8000

# 컨테이너가 시작될 때 실행할 기본 명령어를 설정합니다.
# uvicorn 서버를 실행하여 FastAPI 앱을 띄웁니다.
# --host 0.0.0.0: 외부에서 접속 가능하게 설정
# --port 8000: 내부 포트 8000번 사용
# --reload: 코드 변경 시 서버 자동 재시작 (개발용 옵션)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
