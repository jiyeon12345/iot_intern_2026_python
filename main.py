# ============================================
# 모듈 임포트
# ============================================
import uvicorn  
import os 
from dotenv import load_dotenv

# ============================================
# .env 파일에서 환경변수 로드
# ============================================
load_dotenv()

# ============================================
# 서버 실행 (python main.py 실행시)
# ============================================
def main():
    from app.api import app
    from services.mqtt import start_mqtt_client
    
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    
    # MQTT 클라이언트 시작 (백그라운드 스레드)
    start_mqtt_client()
    print("MQTT 클라이언트가 백그라운드에서 실행 중입니다")
    
    # FastAPI 서버 시작
    print(f"IoT Backend API 서버 시작: http://{host}:{port}")
    print(f"API 문서: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
