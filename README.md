# -SmartNetworkService-AD-Project
25'-2 국민대학교 스마트네트워크서비스 수업 AD 프로젝트

---

## 👥 팀원 정보 (Team Members)

| 이름 | 학번 | 담당 |
|------|------|---------------------------------------------|
| **선현승** | 20203080 | 진단 핸들러, 네트워크 그림판, SFC(Ryu), 윈도우 환경 테스트, 발표 대본 작성 |
| **김아리** | 20223056 | 진단 핸들러, 서버-클라이언트 소켓 통신, 우분투 환경 테스트, 보고서 정리 |

---

## ✅ 요구사항 체크리스트 (16개)

| 번호 | 요구사항 설명 | 구현 여부 | 관련 코드/탭 |
|------|----------------|-----------|----------------|
| 1 | 서버 시작/정지 기능 |  | Server 탭 |
| 2 | 클라이언트 Connect/Disconnect |  | Client 탭 |
| 3 | 고정길이 전송(FIXED) |  | Buffer/Send 탭 |
| 4 | 가변길이 전송(VAR, '\n' 구분) |  | Buffer/Send 탭 |
| 5 | MIX 모드(4바이트 길이 + 본문) |  | Buffer/Send 탭 |
| 6 | 송신 후 close 기능 |  | Client 탭 버튼 |
| 7 | 서버 브로드캐스트 기능 |  | Server 탭 |
| 8 | 그림판(Drawing) 송수신 |  | Draw 탭 |
| 9 | 그림판 브로드캐스트 ON/OFF |  | Draw 탭 |
| 10 | 클라이언트 접속 리스트 표시 |  | Server 탭 |
| 11 | 서버 수신 스레드 처리 |  | recv loop |
| 12 | 클라이언트 수신 스레드 처리 |  | cli_recv_loop |
| 13 | 공유 카운터 + Lock 처리 |  | Server recv |
| 14 | 포트 점유 검사 및 오류 처리 |  | Log 탭 |
| 15 | UI 로그 출력(Server/Client) |  | Log 탭 |
| 16 | 예외 처리(연결 종료, Timeout 등) |  | 전체 |

---

## 🖥️ 실행 방법 (Execution Guide)

Windows 환경:
```bash
python smart_net_suite.py
```

Ubuntu 및 macOS 환경:
```bash
python3 smart_net_suite.py
```

필수 라이브러리(Ubuntu 기준):
```bash
pip install requests
sudo apt-get install python3-tk
```

---

## 🔌 테스트 절차 (Test Procedure)

### 1) 네트워크 진단
- Ping 테스트  
- nslookup 테스트  
- 네트워크 속도 측정  

### 2) 전송 모드 테스트 (FIXED / VAR / MIX 비교)
- FIXED: 정확한 N바이트 송신  
- VAR: '\n' 기준 메시지 구분  
- MIX: 4바이트 길이 + 본문  

---

# 📂 프로그램 탭 소개

---

## 🟦 1. Server 탭
서버 시작/종료, 접속 클라이언트 목록, 서버 로그 표시

📸 스크린샷  
![Server Tab](images/server_tab.png)

설명
- Start/Stop 서버 동작  
- 클라이언트 수 자동 갱신  
- Lock 기반 counter 증가  

---

## 🟩 2. Client 탭
클라이언트 연결/종료 및 송신 테스트

📸 스크린샷  
![Client Tab](images/client_tab.png)

설명
- Connect 클릭 시 서버 접속  
- 송신 후 close 옵션 제공  

---

## 🟧 3. Buffer / Send 탭 (전송 모드)
FIXED / VAR / MIX 모드를 테스트하는 공간

📸 스크린샷  
![Buffer Tab](images/buffer_tab.png)

설명
- 요구사항 11~14번 검증 가능  
- 모드 선택 → 송신 → 서버 로그 확인  

---

## 🟪 4. Draw 탭 (그림판)
마우스를 이용한 실시간 네트워크 그림판

📸 스크린샷  
![Draw Tab](images/draw_tab.png)

설명
- 로컬 + 원격 동시 반영  
- DRAW x1 y1 x2 y2 패킷 구조  
- 그림판 브로드캐스트 ON/OFF 기능  

---

## 🟫 5. Log 탭
각종 서버/클라이언트 로그 표시

📸 스크린샷  
![Log Tab](images/log_tab.png)

설명
- 포트 점유, 연결 종료 등 확인 가능  
- 디버깅 필수 탭  

---

## 📦 프로젝트 구조

```
/SmartNetworkService/
│ smart_net_suite.py
└ README.md
```

---
