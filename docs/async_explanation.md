# 이벤트 루프가 필요한 이유 (Python 초보자용)

## 1. 동기 함수 vs 비동기 함수

### 동기 함수 (Synchronous Function)
```python
def on_message(client, userdata, msg):
    """이것은 동기 함수입니다"""
    data = msg.payload.decode('utf-8')  # 즉시 실행, 완료될 때까지 기다림
    save(data)  # 이것도 즉시 실행, 완료될 때까지 기다림
    print("완료!")  # 순서대로 실행됨
```

**특징:**
- 한 줄씩 순서대로 실행
- 한 작업이 끝나야 다음 작업 시작
- `await` 키워드 사용 안 함

### 비동기 함수 (Asynchronous Function)
```python
async def broadcast_sensor_data(sensor_data: dict):
    """이것은 비동기 함수입니다"""
    json_message = json.dumps(sensor_data)
    await manager.broadcast(json_message)  # await: 이 작업이 끝날 때까지 기다림
    print("완료!")
```

**특징:**
- `async def`로 정의
- `await` 키워드 사용 (다른 작업을 기다릴 때)
- 여러 작업을 동시에 처리 가능 (효율적!)

---

## 2. 문제 상황: 동기 함수에서 비동기 함수 호출

### ❌ 잘못된 방법 (에러 발생!)
```python
def on_message(client, userdata, msg):  # 동기 함수
    processed_data = process_data(raw_data)
    
    # 이렇게 호출하면 에러 발생!
    broadcast_sensor_data(processed_data)  # ❌ TypeError 발생!
```

**에러 메시지:**
```
TypeError: object async_generator can't be used in 'await' expression
```

**이유:**
- `broadcast_sensor_data()`는 `async` 함수라서 **코루틴 객체**를 반환
- 코루틴은 `await`로 실행해야 하는데, 동기 함수에서는 `await` 사용 불가!

### ❌ 이것도 안 됨!
```python
def on_message(client, userdata, msg):
    processed_data = process_data(raw_data)
    
    await broadcast_sensor_data(processed_data)  # ❌ SyntaxError!
    # 동기 함수에서는 await 사용 불가!
```

---

## 3. 이벤트 루프란?

**이벤트 루프 = 비동기 함수들을 실행하는 엔진**

비유하면:
- **동기 함수**: 한 명의 요리사가 요리 하나씩 순서대로 만듦
- **비동기 함수**: 여러 요리사가 동시에 여러 요리 만듦
- **이벤트 루프**: 요리사들을 관리하고 스케줄링하는 매니저

### 이벤트 루프의 역할
1. 비동기 함수들을 실행
2. `await`로 대기 중인 작업들을 관리
3. 다른 작업이 준비되면 전환 (효율적!)

---

## 4. 왜 이벤트 루프가 필요한가?

### 현재 코드 구조:

```
┌─────────────────────────────────────┐
│  FastAPI 서버 (메인 스레드)           │
│  - 이벤트 루프 실행 중                │
│  - WebSocket 연결 관리               │
└─────────────────────────────────────┘
              │
              │
┌─────────────▼───────────────────────┐
│  MQTT 클라이언트 (별도 스레드)         │
│  - 동기 함수로 실행                   │
│  - 이벤트 루프 없음!                  │
│  - on_message() 콜백 실행            │
└─────────────────────────────────────┘
```

**문제:**
- MQTT는 **별도 스레드**에서 실행 (동기 함수)
- FastAPI는 **메인 스레드**에서 실행 (비동기, 이벤트 루프 있음)
- **서로 다른 스레드**이므로 FastAPI의 이벤트 루프를 직접 사용할 수 없음!

**해결책:**
- WebSocket 전용 이벤트 루프를 별도로 만들어서 사용!

---

## 5. 현재 코드 동작 원리

```python
# 1. 전역 이벤트 루프 생성 (한 번만)
_websocket_loop = None

def get_websocket_loop():
    global _websocket_loop
    if _websocket_loop is None:
        # 새 이벤트 루프 생성
        _websocket_loop = asyncio.new_event_loop()
        # 별도 스레드에서 이벤트 루프 실행
        thread = threading.Thread(target=_websocket_loop.run_forever, daemon=True)
        thread.start()
    return _websocket_loop

# 2. MQTT 콜백에서 사용
def on_message(client, userdata, msg):  # 동기 함수
    processed_data = process_data(raw_data)
    
    # 이벤트 루프 가져오기
    loop = get_websocket_loop()
    
    # 다른 스레드의 이벤트 루프에서 비동기 함수 실행
    asyncio.run_coroutine_threadsafe(
        broadcast_sensor_data(processed_data),  # 실행할 비동기 함수
        loop  # 어떤 이벤트 루프에서 실행할지
    )
```

### 단계별 설명:

1. **`get_websocket_loop()`**: 
   - WebSocket 전용 이벤트 루프를 생성하고 별도 스레드에서 실행
   - 한 번만 생성하고 재사용

2. **`asyncio.run_coroutine_threadsafe()`**:
   - 다른 스레드의 이벤트 루프에서 비동기 함수 실행
   - 안전하게 스레드 간 통신

3. **결과**:
   - MQTT 콜백(동기) → 이벤트 루프 → 비동기 함수 실행 ✅

---

## 6. 왜 이렇게 복잡한가?

### 더 간단한 방법은 없나?

#### 방법 1: 모든 것을 동기로? ❌
```python
# WebSocket도 동기로 만들면?
def broadcast_sensor_data(sensor_data):  # 동기 함수
    # 하지만 FastAPI WebSocket은 async만 지원!
    # 불가능!
```

#### 방법 2: 모든 것을 비동기로? ❌
```python
# MQTT도 비동기로?
async def on_message(...):  # 비동기 함수
    # 하지만 paho-mqtt 라이브러리는 동기 콜백만 지원!
    # 불가능!
```

#### 방법 3: 현재 방법 (이벤트 루프) ✅
- MQTT는 동기로 유지 (라이브러리 제약)
- WebSocket은 비동기로 유지 (FastAPI 제약)
- 이벤트 루프로 연결!

---

## 7. 실제 동작 흐름

```
1. MQTT 메시지 수신
   ↓
2. on_message() 콜백 실행 (동기 함수, 별도 스레드)
   ↓
3. 데이터 처리 및 DB 저장
   ↓
4. get_websocket_loop() 호출 → 이벤트 루프 가져오기
   ↓
5. asyncio.run_coroutine_threadsafe() 호출
   ↓
6. 이벤트 루프가 broadcast_sensor_data() 실행 (비동기)
   ↓
7. manager.broadcast() 실행 → 모든 WebSocket 클라이언트에 전송
   ↓
8. 완료!
```

---

## 8. 핵심 정리

### 왜 이벤트 루프가 필요한가?

1. **MQTT 콜백은 동기 함수** (paho-mqtt 라이브러리 제약)
2. **WebSocket 함수는 비동기 함수** (FastAPI 제약)
3. **동기 함수에서 비동기 함수를 직접 호출할 수 없음**
4. **이벤트 루프가 비동기 함수를 실행하는 엔진**
5. **따라서 이벤트 루프를 통해 비동기 함수를 실행해야 함!**

---

## 9. 참고 자료

- Python 공식 문서: https://docs.python.org/3/library/asyncio.html
- FastAPI WebSocket: https://fastapi.tiangolo.com/advanced/websockets/

