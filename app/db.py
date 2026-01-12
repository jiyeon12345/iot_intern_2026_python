# ============================================
# 모듈 임포트
# ============================================
import os # 환경변수 처리
from sqlalchemy import create_engine, text # SQLAlchemy 모듈
from datetime import datetime # 날짜 시간 처리
from dotenv import load_dotenv # 환경변수 처리

# ============================================
# .env 파일에서 환경변수 읽기
# ============================================
load_dotenv()

# ============================================
# 데이터베이스 연결 설정
# ============================================
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST')
mysql_port = os.getenv('MYSQL_PORT')
mysql_database = os.getenv('MYSQL_DATABASE')

# MySQL 연결 문자열 만들기
mysql_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"

# 데이터베이스 엔진 생성
engine = create_engine(mysql_url)

# 테이블 이름
TABLE_NAME = os.getenv('MYSQL_TABLE_NAME', 'sensor') # 테이블 이름

# ============================================
# 데이터베이스 쿼리 함수
# ============================================
# 센서 데이터 목록 조회
# parameters: limit (조회할 최대 개수)
# ============================================
def find_all(limit=100): 
    sql = text(f"""
        SELECT sensor_id, sensor_nm, temperature, humidity, create_dt 
        FROM {TABLE_NAME} 
        ORDER BY create_dt DESC 
        LIMIT :limit
    """)
    params = {'limit': limit}
    
    # 데이터베이스에서 데이터 가져오기
    with engine.connect() as conn:
        result = conn.execute(sql, params)
        rows = result.fetchall()
    
    # 결과를 딕셔너리 리스트로 변환
    data_list = []
    for row in rows:
        data_list.append({
            "sensor_id": row[0],
            "sensor_nm": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "create_dt": row[4]
        })
    
    return data_list

# ============================================
# 센서 데이터 저장
# parameters: sensor_nm (센서 이름), temperature (온도), humidity (습도)
# ============================================
def save(sensor_nm: str, temperature: float, humidity: float):
    create_dt = datetime.now()
    
    # 고유한 sensor_id 생성 (센서이름_타임스탬프)
    unique_sensor_id = f"{sensor_nm}_{create_dt.strftime('%Y%m%d%H%M%S')}"
    
    # SQL 쿼리 작성
    sql = text(f"""
        INSERT INTO {TABLE_NAME} (sensor_id, sensor_nm, temperature, humidity, create_dt) 
        VALUES (:sensor_id, :sensor_nm, :temperature, :humidity, :create_dt)
    """)
    
    # 데이터베이스에 저장
    with engine.connect() as conn:
        conn.execute(sql, {
            'sensor_id': unique_sensor_id,
            'sensor_nm': sensor_nm,
            'temperature': temperature,
            'humidity': humidity,
            'create_dt': create_dt
        })
        conn.commit()
    
    print(f"데이터 저장 완료: {sensor_nm} - 온도:{temperature}, 습도:{humidity}")

