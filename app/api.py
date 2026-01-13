from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.db import find_all
from services.websocket import manager
import os
import asyncio
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(title="IoT Backend API", version="1.0.0")

# CORS 설정
portal_url = os.getenv('PORTAL_URL')
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

# ============================================
# WebSocket 엔드포인트
# ============================================
# 실시간 센서 데이터 수신용 WebSocket
# 사용예시: ws://localhost:8000/ws/sensor/realtime
# ============================================
@app.websocket("/ws/sensor/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """실시간 센서 데이터를 받기 위한 WebSocket 엔드포인트"""
    await manager.connect(websocket)
    try:
        # 클라이언트가 연결을 유지하는 동안 대기
        # 서버에서 클라이언트로만 데이터를 보내므로, 클라이언트 메시지 수신은 선택사항
        while True:
            # 클라이언트로부터 메시지 수신 대기 (없어도 연결은 유지됨)
            # 클라이언트가 메시지를 보내지 않으면 여기서 대기 상태로 유지
            try:
                data = await websocket.receive_text()
                # 클라이언트로부터 메시지가 오면 처리 (선택사항)
                print(f"클라이언트로부터 메시지 수신: {data}")
            except Exception as e:
                # 연결이 끊어졌거나 오류 발생 시 루프 종료
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket 오류: {e}")
        manager.disconnect(websocket)
