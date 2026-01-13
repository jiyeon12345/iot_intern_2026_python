# ============================================
# 모듈 임포트
# ============================================
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from app.db import save
from services.websocket import broadcast_sensor_data
import asyncio
import threading
# ============================================
# .env 파일에서 환경변수 읽기
# ============================================
load_dotenv()

# ============================================
# MQTT 설정
# ============================================
MQTT_BROKER_IP = os.getenv('MQTT_BROKER_IP', 'localhost')
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', 1883))
CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'iot_backend_client')
MQTT_TOPIC = os.getenv('MQTT_TOPIC', '/oneM2M/req/+/+/json')

# ============================================
# 데이터 가공
# ============================================
def process_data(raw_data: str) -> dict:
    """
    oneM2M 형식의 MQTT 메시지를 파싱하여 센서 데이터 추출
    """
    try:
        # 1. oneM2M 메시지 파싱
        onem2m_msg = json.loads(raw_data)
        
        # 2. 센서 데이터 추출 (m2m:rqp.pc.m2m:cin.con 안에 있음)
        sensor_data_str = onem2m_msg.get('m2m:rqp', {}).get('pc', {}).get('m2m:cin', {}).get('con', '{}')
        sensor_data = json.loads(sensor_data_str)
        
        # 3. sensor_id 추출 (m2m:rqp.to 경로에서)
        sensor_path = onem2m_msg.get('m2m:rqp', {}).get('to', '')
        sensor_path_parts = sensor_path.split('/')
        sensor_nm = sensor_path_parts[3] if len(sensor_path_parts) > 3 else "unknown"
        
        # 4. 가공된 데이터 반환
        return {
            'sensor_nm': sensor_nm,
            'humidity': sensor_data.get('humidity'),
            'temperature': sensor_data.get('temperature')
        }
        
    except Exception as e:
        print(f"데이터 파싱 실패: {e}")
        return None

# ============================================
# MQTT 연결 성공 시 호출
# ============================================
def on_connect(client, userdata, flags, rc):
    """MQTT 연결 성공 시 호출"""
    if rc == 0:
        print(f"MQTT 브로커 연결 성공: {MQTT_BROKER_IP}:{MQTT_BROKER_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"토픽 구독: {MQTT_TOPIC}")
    else:
        print(f"MQTT 연결 실패: {rc}")


# ============================================
# MQTT 메시지 수신 시 호출
# ============================================
def on_message(client, userdata, msg):
    """MQTT 메시지 수신 시 호출"""
    try:
        # 1. 메시지 디코딩
        raw_data = msg.payload.decode('utf-8')
        print(f"메시지 수신: {msg.topic}")
        
        # 2. 데이터 가공 (oneM2M 파싱)
        processed_data = process_data(raw_data)
        
        # 3. 파싱 실패 시 종료
        if not processed_data:
            return
        
        # 4. Repository를 통해 데이터베이스에 저장
        save(
            sensor_nm=processed_data['sensor_nm'],
            temperature=processed_data['temperature'],
            humidity=processed_data['humidity']
        )

        # 5. 센서 데이터를 WebSocket으로 브로드캐스트
        #
        # [동작 원리]
        # 1. get_websocket_loop() → WebSocket 전용 이벤트 루프 가져오기
        # 2. asyncio.run_coroutine_threadsafe() → 다른 스레드의 이벤트 루프에서 실행
        # 3. broadcast_sensor_data() → 비동기로 실행되어 모든 WebSocket 클라이언트에 전송
        # 참고 : async_example.md 참고
        try:
            loop = get_websocket_loop()  # 이벤트 루프 가져오기
            # 다른 스레드의 이벤트 루프에서 비동기 함수 실행
            asyncio.run_coroutine_threadsafe(broadcast_sensor_data(processed_data), loop)
        except Exception as e:
            print(f"WebSocket 브로드캐스트 오류: {e}")
        
    except Exception as e:
        print(f"메시지 처리 오류: {e}")

# ============================================
# MQTT 클라이언트 생성 및 시작 함수
# ============================================
def start_mqtt_client():
    """
    MQTT 클라이언트를 백그라운드 스레드에서 실행
    Spring의 @Component처럼 애플리케이션 시작 시 자동 실행
    """
    import threading
    
    mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=CLIENT_ID)
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    
    def run_mqtt():
        try:
            mqttClient.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT)
            print("MQTT 클라이언트 시작...")
            mqttClient.loop_forever() # 무한 루프로 메시지 수신 대기
        except Exception as e:
            print(f"MQTT 오류 발생: {e}")
    
    # 백그라운드 스레드에서 MQTT 실행
    mqtt_thread = threading.Thread(target=run_mqtt, daemon=True)
    mqtt_thread.start()
    return mqttClient

# ============================================
# 전역 이벤트 루프 (WebSocket 브로드캐스트용)
# ============================================
# [이벤트 루프란?]
# - 비동기 함수(async def)들을 실행하는 엔진
# - await로 대기 중인 작업들을 관리하고 스케줄링
# - Vue(JavaScript)도 이벤트 루프 사용 (자동 제공)
# - Python도 이벤트 루프 사용 (명시적 생성 필요)
# [동작 방식]
# 1. 첫 호출 시: 새 이벤트 루프 생성 → 별도 스레드에서 실행 시작
# 2. 이후 호출: 이미 생성된 이벤트 루프 반환 (재사용)
# ============================================
_websocket_loop = None

def get_websocket_loop():
    global _websocket_loop
    if _websocket_loop is None:
        # 1. 새 이벤트 루프 생성
        _websocket_loop = asyncio.new_event_loop()
        # 2. 별도 스레드에서 이벤트 루프 실행 (무한 루프)
        thread = threading.Thread(target=_websocket_loop.run_forever, daemon=True)
        thread.start()
        print("WebSocket 이벤트 루프 시작됨")
    return _websocket_loop

# ============================================
# 직접 실행 시 (독립 실행용)
# ============================================
if __name__ == "__main__":
    mqttClient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id=CLIENT_ID)
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    
    try:
        mqttClient.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT)
        print("MQTT 클라이언트 시작...")
        mqttClient.loop_forever()
    except KeyboardInterrupt:
        print("\nMQTT 클라이언트 종료")
        mqttClient.disconnect()
    except Exception as e:
        print(f"오류 발생: {e}")
