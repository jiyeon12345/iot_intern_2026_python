# ThingsBoard 장치 설정 가이드

## 1. ThingsBoard 접속
- URL: `http://localhost:8083` (또는 설정한 TB_HOST)
- 로그인: `tenant@thingsboard.org` / `tenant` (또는 관리자 계정)

## 2. 장치(Device) 생성

### 2-1. 장치 생성
1. 왼쪽 메뉴에서 **"device | 장치"** 클릭
2. 우측 상단 **"+"** 버튼 클릭
3. **"Add new device | 장치 추가"** 선택
4. 장치 정보 입력:

   **필수 항목 (반드시 입력):**
   - **이름**: `SensorData` 입력 (센서 이름과 동일하게! 이게 장치 이름입니다)
   - **라벨 (Label)**: `SensorData` 입력 (센서 이름과 동일하게! )
   - **장치 프로파일 (Device Profile)**: `default` 그대로 사용 (별표 * 표시 = 필수)

   **선택 항목 (무시해도 됨):**
   - **게이트웨이 여부**: 꺼둔 상태 그대로 (일반 센서는 게이트웨이 아님)
   - **커스터머에게 할당**: 비워두거나 무시 (조직 관리용, 데이터 전송과 무관)

6. **"추가"** 버튼 클릭

> 💡 **요약**: 라벨에 `SensorData`만 입력하고 나머지는 기본값 그대로 두면 됩니다!

</br>
<img width="688" height="765" alt="image" src="https://github.com/user-attachments/assets/f18cd594-c1c4-458b-8501-26a4f5596d29" />
</br>

### 2-2. Access Token 복사
1. 생성된 장치를 클릭하여 상세 페이지로 이동
2. 상단 탭에서 **"Credentials | 자격 증명 관리"** 클릭
3. **"Access token"** 섹션에서 토큰 값 복사
   - 예: `A1_TEST_TOKEN_12345678`
4. 또는 엑세스 토큰 복스 클릭
    
</br>
<img width="499" height="295" alt="image" src="https://github.com/user-attachments/assets/7c9470ea-132e-47b4-9a67-77af13a1f329" />
</br>

## 3. 코드에 토큰 추가

`services/mqtt.py` 파일의 `TB_TOKENS` 딕셔너리에 센서 이름과 토큰을 매핑하세요:

```python
TB_TOKENS = {
    "SensorData": "여기에_복사한_토큰_붙여넣기",
}
```

## 4. 데이터 확인

### 4-1. 실시간 데이터 확인
1. ThingsBoard에서 장치 페이지로 이동
2. **"Latest telemetry | 최근 데이터 "** 탭에서 실시간 데이터 확인
   - `temperature`, `humidity` 값이 표시됩니다
</br>
<img width="499" height="295" alt="image" src="https://github.com/user-attachments/assets/8356e02a-bd0a-4cbd-a69c-ebe96b5787c3" />
</br>
</br>

### 4-2. 대시보드 생성 (선택사항)
1. 왼쪽 메뉴에서 **"Dashboards"** 클릭
2. **"+"** 버튼으로 새 대시보드 생성
3. 위젯 추가하여 차트/그래프로 데이터 시각화
- 참고 링크 : https://thingsboard.io/docs/getting-started-guides/helloworld/#step-3-create-dashboard

## 5. 문제 해결

### 토큰이 없어서 전송이 안 될 때
- 콘솔에 `[SensorData]에 매칭되는 ThingsBoard 토큰이 없습니다. 전송 스킵.` 메시지 확인
- `TB_TOKENS`에 `"SensorData"` 키가 있는지 확인
- 토큰 값이 정확한지 확인

### 연결 오류가 발생할 때
- ThingsBoard가 실행 중인지 확인: `docker ps` 또는 브라우저에서 접속 확인
- `TB_HOST` 환경변수가 올바른지 확인 (`.env` 파일)
- 방화벽 설정 확인 (포트 8083)

### 데이터가 안 보일 때
- ThingsBoard 장치 페이지에서 **"Latest telemetry"** 탭 확인
- MQTT 메시지가 정상적으로 수신되는지 콘솔 로그 확인
- ThingsBoard 전송 성공 메시지 확인: `ThingsBoard 전송 성공: [SensorData]`
