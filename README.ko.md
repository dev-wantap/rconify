# RCONify - RCON Bridge for Minecraft Bedrock Dedicated Server

RCONify는 RCON(Remote Console) 프로토콜을 기본적으로 지원하지 않는 Minecraft Bedrock Edition 서버에 RCON 기능을 제공하는 파이썬 기반 브릿지(Bridge) 서버입니다.

이 프로젝트는 `screen` 세션에서 실행 중인 Bedrock 서버에 원격으로 명령을 실행하고 그 결과를 받아올 수 있도록 해줍니다.

## 주요 기능

-   **RCON 지원**: RCON 클라이언트(`mcrcon` 등)를 사용하여 Bedrock 서버에 연결하고 명령을 실행할 수 있습니다.
-   **Screen 연동**: `screen` 유틸리티를 사용하여 실행 중인 서버 콘솔과 상호작용합니다.
-   **응답 파싱**: 서버의 전체 화면 출력에서 명령어에 대한 실제 응답만 지능적으로 파싱하여 반환합니다.
-   **순수 Python**: 별도의 외부 라이브러리 없이 Python 표준 라이브러리만으로 작동합니다.

## 동작 원리

1.  RCONify 서버가 지정된 포트(기본값: 25575)에서 RCON 클라이언트의 연결을 기다립니다.
2.  클라이언트가 인증 후 명령어를 전송하면, RCONify는 `screen -X stuff` 명령을 통해 해당 명령어를 Bedrock 서버의 콘솔에 입력합니다.
3.  잠시 후, `screen -X hardcopy` 명령으로 현재 화면 전체를 텍스트 파일로 캡처합니다.
4.  캡처된 텍스트(서버 로그, 명령어, 결과 등이 섞여 있음)에서 방금 실행한 명령어에 대한 응답 부분만 파싱합니다.
5.  추출된 결과를 RCON 프로토콜에 맞춰 클라이언트에게 다시 전송합니다.

## 요구사항

-   Python 3.x
-   `screen` 유틸리티
-   `screen` 세션 내에서 실행되고 있는 Minecraft Bedrock 서버

## 설치 및 사용법

1.  **저장소 복제:**
    ```bash
    git clone https://github.com/dev-wantap/rconify.git
    cd rconify
    ```

2.  **RCONify 서버 실행:**
    `main.py`를 실행하고, 인자로 Bedrock 서버가 실행 중인 `screen` 세션의 이름을 전달합니다.

    ```bash
    python3 main.py <screen_session_name>
    ```
    *   예시: `screen` 세션 이름이 `bedrock`인 경우
        ```bash
        python3 main.py bedrock
        ```

3.  **RCON 클라이언트로 연결:**
    이제 `mcrcon`과 같은 RCON 클라이언트를 사용하여 서버에 연결할 수 있습니다.

    ```bash
    mcrcon -H 127.0.0.1 -P 25575 -p password "list"
    ```
    *   기본 비밀번호는 `password` 입니다. (소스 코드 `rcon_server.py`에서 변경 가능)

## 설정

RCON 서버의 호스트, 포트, 비밀번호는 `rcon_server.py` 파일 상단에서 직접 수정할 수 있습니다.

```python
# rcon_server.py

class RCONServer:
    def __init__(self, screen_handler, host='0.0.0.0', port=25575, password='password'):
        # ...
```
