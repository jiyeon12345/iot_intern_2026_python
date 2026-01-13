import json
from typing import Set
from fastapi import WebSocket

# ============================================
# WebSocket 연결 관리자
# ============================================
class ConnectionManager:
    """WebSocket 연결된 클라이언트들을 관리하는 클래스"""
    
    def __init__(self):
        # 연결된 클라이언트들을 저장하는 Set
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """클라이언트 연결 시 호출"""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"WebSocket 클라이언트 연결됨. 현재 연결 수: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """클라이언트 연결 해제 시 호출"""
        self.active_connections.discard(websocket)
        print(f"WebSocket 클라이언트 연결 해제됨. 현재 연결 수: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """특정 클라이언트에게만 메시지 전송"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"메시지 전송 실패: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """연결된 모든 클라이언트에게 메시지 브로드캐스트"""
        if not self.active_connections:
            return
        
        # 연결이 끊어진 클라이언트들을 제거하기 위한 리스트
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"브로드캐스트 실패 (연결 해제됨): {e}")
                disconnected.append(connection)
        
        # 끊어진 연결 제거
        for connection in disconnected:
            self.disconnect(connection)

# 전역 ConnectionManager 인스턴스
manager = ConnectionManager()

# # ============================================
# # 센서 데이터를 WebSocket으로 브로드캐스트하는 함수
# # ============================================
async def broadcast_sensor_data(sensor_data: dict):
    """
    MQTT에서 받은 센서 데이터를 연결된 모든 WebSocket 클라이언트에게 전송
    
    Args:
        sensor_data: 센서 데이터 딕셔너리 (sensor_nm, temperature, humidity 포함)
    """
    try:
        # 딕셔너리를 JSON 문자열로 변환
        json_message = json.dumps(sensor_data, ensure_ascii=False, default=str)
        # 모든 연결된 클라이언트에게 브로드캐스트
        await manager.broadcast(json_message)
        print(f"센서 데이터 브로드캐스트 완료: {sensor_data.get('sensor_nm', 'unknown')}")
    except Exception as e:
        print(f"센서 데이터 브로드캐스트 실패: {e}")


# ============================================
# 참고 url : https://leapcell.io/blog/ko/fastapi-wa-websoket-eul-yonghan-python-sil-sigan-tongsin
# ============================================