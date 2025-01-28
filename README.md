# Winection API
양방향 수어 번역 화상채팅 서비스 API

<br>

## 📖 실행 방법
실행 방법은 cli 기준으로 작성하였습니다.

다른 GUI나 IDE를 사용하는 분들은 각자의 방법에 맞춰서 실행하면 됩니다.

<br>

### 🔖 세팅
새로운 터미널을 실행한다.

`git clone https://github.com/DongUgaUga/winection-api.git`를 통해 클론킨다.

`cd winection-api` winection-api 디렉터리로 이동한다.

<br>

### 🔖 백엔드 실행
main.py 실행 명령어
- `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

<br>

### 🔖 프론트엔드 실행

새로운 터미널을 실행한다.

`cd winection-api/test_front` test_front 디렉터리로 이동한다.

test.html 실행 명령어(테스트용 프론트엔드)
- `python3 -m http.server 8080 --bind 0.0.0.0`

<br>

### 🔖 웹 실행
> **Mac/Linux OS**
> - `ifconfig | grep "inet " | grep -v 127.0.0.1`을 통해 main.py를 실행시킨 서버의 IP주소를 알아낸다.

> **Window OS**
> - `ipconfig`을 통해 main.py를 실행시킨 서버의 IP주소를 알아낸다.
> - 자신이 사용하고 있는 인터넷 환경(이더넷, WIFI 등)의 IPv4 Address를 확인한다.

<br>

크롬에 들어가서 <서버IP주소>:8080/test.html 접속

다른 클라이언트로 동일한 방법으로 실행
> 현재는 NAT 처리를 안해서 동일한 NAT 환경(같은 WIFI 또는 같은 네트워크 환경)에서만 통신이 가능하다.
