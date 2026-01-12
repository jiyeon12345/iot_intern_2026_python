from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.db import find_all
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(title="IoT Backend API", version="1.0.0")

# CORS 설정
portal_url = os.getenv('PORTAL_URL', 'http://localhost:5173')
allow_origins = [url.strip() for url in portal_url.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# ============================================
# 응답 형식 정의
# parameters: sensor_id (센서 ID), sensor_nm (센서 이름), temperature (온도), humidity (습도), create_dt (생성 시간)
# ============================================
class IoTDataResponse(BaseModel):
    sensor_id: str
    sensor_nm: str
    temperature: float
    humidity: float
    create_dt: datetime

# ============================================
# API 엔드포인트
# ============================================
# 센서 데이터 목록 조회
# parameters: limit (조회할 최대 개수)
# 사용예시: /api/sensors?limit=100
# ============================================
@app.get("/api/sensors", response_model=List[IoTDataResponse])
def get_iot_data_list(
    limit: int = 100
):
    try:
        data_list = find_all(limit=limit)
        return data_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
