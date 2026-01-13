# ============================================
# 예시 1: 동기 함수 (일반 함수)
# ============================================
def sync_function():
    """동기 함수 - 순서대로 실행"""
    print("1. 첫 번째 작업")
    print("2. 두 번째 작업")
    print("3. 세 번째 작업")
    # 한 줄씩 순서대로 실행됨

# ============================================
# 예시 2: 비동기 함수
# ============================================
import asyncio

async def async_function():
    """비동기 함수 - await로 다른 작업 기다림"""
    print("1. 첫 번째 작업")
    await asyncio.sleep(1)  # 1초 대기 (다른 작업 가능)
    print("2. 두 번째 작업")
    await asyncio.sleep(1)  # 1초 대기
    print("3. 세 번째 작업")

# 비동기 함수 실행 방법
# asyncio.run(async_function())  # 이벤트 루프 생성하고 실행

# ============================================
# 예시 3: 동기 함수에서 비동기 함수 호출 (에러!)
# ============================================
def sync_calling_async():
    """동기 함수에서 비동기 함수 호출 시도"""
    # ❌ 이렇게 하면 에러!
    # async_function()  # TypeError 발생!
    
    # ❌ 이것도 에러!
    # await async_function()  # SyntaxError! (동기 함수에서 await 사용 불가)
    
    # ✅ 올바른 방법: 이벤트 루프 사용
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_function())
    loop.close()

# ============================================
# 예시 4: 현재 코드와 유사한 구조
# ============================================
import threading

# 전역 이벤트 루프
_loop = None

def get_loop():
    """이벤트 루프 가져오기 (한 번만 생성)"""
    global _loop
    if _loop is None:
        _loop = asyncio.new_event_loop()
        # 별도 스레드에서 실행
        thread = threading.Thread(target=_loop.run_forever, daemon=True)
        thread.start()
    return _loop

def sync_function_calling_async():
    """동기 함수에서 비동기 함수 호출 (현재 코드와 유사)"""
    loop = get_loop()  # 이벤트 루프 가져오기
    
    # 다른 스레드의 이벤트 루프에서 비동기 함수 실행
    asyncio.run_coroutine_threadsafe(async_function(), loop)

# ============================================
# 비교: 동기 vs 비동기
# ============================================
"""
동기 함수:
- 한 번에 하나의 작업만 처리
- 작업이 끝날 때까지 기다림
- 간단하지만 느릴 수 있음

비동기 함수:
- 여러 작업을 동시에 처리 가능
- await로 대기 중에도 다른 작업 가능
- 복잡하지만 빠름 (I/O 작업에 유리)
"""

# ============================================
# 실제 사용 예시 (현재 프로젝트)
# ============================================
"""
# MQTT 콜백 (동기 함수)
def on_message(client, userdata, msg):
    data = process_data(msg.payload)
    
    # 이벤트 루프를 통해 비동기 함수 실행
    loop = get_websocket_loop()
    asyncio.run_coroutine_threadsafe(
        broadcast_sensor_data(data),  # 비동기 함수
        loop  # 이벤트 루프
    )

# WebSocket 브로드캐스트 (비동기 함수)
async def broadcast_sensor_data(data):
    await manager.broadcast(json.dumps(data))
"""

