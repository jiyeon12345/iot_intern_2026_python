# IoT Python Backend

## 프로젝트 설정

### 1. 가상환경 생성 및 활성화

> **왜 가상환경이 필요한가요?**
> 
> - **Node**: `node_modules`가 프로젝트 폴더 안에 있어서 자동 격리
> - **Python**: 전역(시스템)에 라이브러리를 설치하면 **모든 프로젝트가 공유**됨
> 
> **가상환경 사용 시:**
> - 각 프로젝트마다 독립적인 라이브러리 환경
> - 버전 충돌 없음 
> - 다른 사람과 협업 시 동일한 환경 보장

```bash
# 가상환경 생성
python -m venv venv

# Windows에서 활성화
venv\Scripts\activate

# Linux/Mac에서 활성화
source venv/bin/activate

# 가상환경 비활성화 (필요시)
deactivate
```


### 2. 의존성 설치

> **왜 requirements.txt가 필요한가요?**
> 
> - **Node**: `package.json`에 의존성 정의 → `npm install`로 자동 설치
> - **Python**: `requirements.txt`에 의존성 정의 → `pip install -r requirements.txt`로 수동 설치
> 

```bash
# requirements.txt에 있는 모든 라이브러리 설치
pip install -r requirements.txt

# 설치한 라이브러리 목록을 requirements.txt에 저장
pip freeze > requirements.txt
```

### 3. 환경변수 설정 (.env 파일 생성)

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# MQTT 설정
MQTT_BROKER_IP=localhost
MQTT_BROKER_PORT=1883
MQTT_CLIENT_ID=iot_backend_client
# oneM2M 토픽 형식: /oneM2M/req/${AE}/${CseId}/json
MQTT_TOPIC=/oneM2M/req/+/+/json

# MySQL 설정
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=iot_db

# FastAPI 설정
API_HOST=0.0.0.0
API_PORT=8000
```

### 4. 프로젝트 실행
```bash
python main.py
```

**API 문서 확인:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**전체 동작 흐름:**
1. `python main.py` 실행 → FastAPI 서버 + MQTT 클라이언트 동시 시작
2. MQTT 클라이언트가 메시지 수신 → DB에 저장 (백그라운드)
3. API 서버가 DB에서 데이터 조회 → `/api/data` 엔드포인트로 제공


## 프로젝트 구조

```
iot_python_backend/
├── venv/                  # 가상환경 (git에 포함되지 않음)
├── app/                   # 애플리케이션 코드
│   ├── __init__.py
│   ├── api.py            # API 엔드포인트
│   └── db.py             # 데이터베이스 연결 및 쿼리
├── services/              # 외부 서비스 연동
│   ├── __init__.py
│   └── mqtt.py           # MQTT 데이터 수신 및 MySQL 저장
├── main.py                # FastAPI 서버 실행
├── requirements.txt       # 의존성 목록
├── .env                   # 환경변수 (git에 포함되지 않음)
├── .gitignore            # Git 제외 파일
└── README.md             # 프로젝트 설명
```

## 주요 기능

1. **MQTT 데이터 수신** (`services/mqtt.py`)
   - oneM2M 형식의 MQTT 메시지 수신
   - 토픽 형식: `/oneM2M/req/${AE}/${CseId}/json`
   - oneM2M 메시지에서 센서 데이터 추출 (pillar_id, humidity, temperature)
   - MySQL에 저장

2. **목록 조회 API** (`app/api.py`)
   - `GET /api/data` - 전체 목록 조회
     - `device_id`: 디바이스 ID로 필터링
     - `pillar_id`: 기둥 ID로 필터링 (예: PILLAR_001)
     - `limit`, `offset`: 페이징
   - `GET /api/data/{data_id}` - 특정 데이터 조회

## oneM2M 메시지 형식

```json
{
  "m2m:rqp": {
    "pc": {
      "m2m:cin": {
        "con": "{\"pillar_id\":\"PILLAR_001\",\"timestamp\":\"...\",\"humidity\":5.2,\"temperature\":25.1}"
      }
    }
  }
}
```
