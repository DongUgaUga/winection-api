# Winection API
양방향 수어 번역 화상채팅 서비스 API

<br>

## 📖 실행 방법
실행 방법은 bash CLI 기준으로 작성하였습니다.

다른 GUI나 IDE를 사용하는 분들은 각자의 방법에 맞춰서 실행하면 됩니다.

<br>

### 🔖 세팅
새로운 터미널을 실행
```bash
# 해당 레포지토리 클론
git clone https://github.com/DongUgaUga/winection-api.git

# 레포지토리로 디렉터리 이동
cd winection-api
````

> 현재는 키 인증에 필요한 파일이 빠져있어 제대로 실행이 안된다.  
> .env을 넣어줘야한다.  
> 필요한 사람은 프로젝트 노션 문서에 있으니 확인
> https://www.notion.so/woodong222/API-Key-https-1896be62840280d9b79fca3e4bd44267?pvs=4

<br>

### 🔖 서버 실행

```bash
# 실행 권한 부여
chmod +x run.sh  

# 스크립트 실행
./run.sh  
```

서버 종료: `Ctrl`+`C`

<br>

### 🔖 웹 실행
./run.sh을 실행시킨 서버의 IP주소 카피

**Mac/Linux OS**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1`
```

**Window OS**
```bash
## 자신이 사용하고 있는 인터넷 환경(이더넷, WIFI 등)의 IPv4 Address 카피
ipconfig 
```
<br>

### 🔖 접속 방법 
크롬 브라우저에 아래 URL을 입력하여 접속

> 화상채팅 테스트
> ```
> http://<서버IP주소>:8080/front/rtc.html
> ```
> 다른 클라이언트로 동일한 방법으로 URL 접속
>>  현재는 NAT 처리를 안해서 동일한 NAT 환경(같은 WIFI 또는 같은 네트워크 환경)에서만 통신이 가능하다.  
>> chrome://flags/#unsafely-treat-insecure-origin-as-secure에서 세팅을 해줘야 웹캠, 마이크 가능  
>> 참고링크: https://velog.io/@juna-dev/navigator.mediaDevices-undefined-%ED%95%B4%EA%B2%B0  
>> 위의 링크에서 <IP주소>:8080 입력

<br>

> SLTS (Sign Language-To-Speech) 과정 중 단어 -> 문장 -> TTS 테스트
> ```
> http://<서버IP주소>:8080/front/slts.html
> ```


<br>


## 📖 프로젝트 구조 개요
```
/winection-api                   
    ├── README.md   
    ├── front                  
    │   ├── package-lock.json               
    │   ├── package.json                
    │   ├── rtc.html                        # 화상채팅 프론트엔드(테스트용)
    │   └─── stsl.html                      # word -> sentence -> speech 프론트엔드(테스트용)  
    ├── .gitignore   
    ├── requirements.txt  
    ├── run.sh                              # 실행 스크립트 
    ├── secret
    │   └── google-cloud-api-key.json       
    └── src                                  
        ├── app.py                              
        └── ws  
            ├── ws_server.py                # WebSocket 관련  
            ├── stsl_server.py              # stsl WebSocket 관련    
            ├── slts                             
            │   ├── sentence.py             # 수어 단어 -> 문장 병합
            │   ├── speech.py               # 문장 텍스트 -> 음성 변환
            │   └── word.py                 # 손 좌표 -> 수어 단어 변환
            └── stsl
                ├── sign.py                 # 텍스트 -> 손 좌표 변환
                └── word.py                 # 텍스트 -> 단어로 분할
```