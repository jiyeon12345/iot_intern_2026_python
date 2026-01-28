***시작하는 법!!!***
## 1. 사전 준비

* **Docker Desktop 설치:** [공식 홈페이지](https://www.docker.com/products/docker-desktop/)에서 설치하고, 설정에서 **WSL 2 기반 엔진**이 활성화되어 있는지 확인하세요.
* **터미널 실행:** PowerShell 또는 명령 프롬프트(CMD)를 엽니다.

## 2. 데이터 보존을 위한 볼륨 생성

컨테이너를 삭제해도 데이터가 날아가지 않도록 저장 공간(Volume)을 미리 만들어야 합니다.

```powershell
docker volume create mytb-data
docker volume create mytb-logs

```

## 3. ThingsBoard 실행 (Docker Compose 방식)

가장 관리하기 쉬운 `docker-compose.yml` 파일을 이용한 방법입니다. 적당한 폴더를 만들고 그 안에 아래 내용을 담은 파일을 생성하세요.

### `docker-compose.yml` 작성

```yaml
version: '3.0'
services:
  mytb:
    restart: always
    image: "thingsboard/tb-postgres"
    ports:
      - "8083:9090"
      - "1883:1883"
      - "7070:7070"
      - "5683-5688:5683-5688/udp"
    environment:
      TB_QUEUE_TYPE: in-memory
    volumes:
      - mytb-data:/data
      - mytb-logs:/var/log/thingsboard
volumes:
  mytb-data:
    external: true
  mytb-logs:
    external: true

```

### 컨테이너 실행

해당 폴더에서 아래 명령어를 입력합니다.

```powershell
docker-compose up -d

```


<img width="1692" height="377" alt="image" src="https://github.com/user-attachments/assets/d9fb92e8-96b8-405d-9d39-e62eb440ddec" />
이미지가 위와 같이 뜨면 문제가 없는겁니다.



<img width="309" height="58" alt="image" src="https://github.com/user-attachments/assets/a5c48c73-274e-4075-a521-8d744a9e28f2" />
<img width="1663" height="71" alt="image" src="https://github.com/user-attachments/assets/4b0d9860-7218-40ff-89d8-b90dce71fce1" />
위와 같이 컨테이너에서 띵스보드가 running 상태여야 작업이 가능합니다.


> **참고:** 처음 실행 시 이미지를 다운로드하고 데이터베이스를 초기화하는 데 시간이 몇 분 정도 걸립니다.

## 4. 접속 및 확인

설치가 완료되면 브라우저를 열고 다음 주소로 접속합니다.

* **URL:** `http://localhost:8083`

로그인을 위해 제공되는 기본 공용 계정은 다음과 같습니다:

* **관리자(System Admin):** `sysadmin@thingsboard.org` / 암호: `sysadmin`
* **테넌트(Tenant Admin):** `tenant@thingsboard.org` / 암호: `tenant`
