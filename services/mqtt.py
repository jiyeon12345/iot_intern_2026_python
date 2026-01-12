# ============================================
# 모듈 임포트
# ============================================
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from app.db import save

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
