# smart_net_suite_skeleton.py
# 통합 네트워크/SFC GUI 스켈레톤 (기능 비워둔 틀)
# - 실행은 되지만 실제 네트워크/REST 동작 없음
# - 각 TODO 지점에 구현을 채워 넣으세요.
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess   # ipconfig 사용
import platform     # 윈도우, 맥/리눅스 구별
import socket       # 소켓함수 사용
import struct       # 64비트 변환
import threading

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("스마트 네트워크 서비스 — 스켈레톤")
        self.geometry("1100x720")
        self.server_running = False
        self.client_connected = False
        self.counter_lock = threading.Lock() # 접속한 클라이언트의 수 (공유 카운터)
        self.server_stop_event = threading.Event() # 안전 종료
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True)
        self.pg_diag = ttk.Frame(nb); nb.add(self.pg_diag, text="네트워크 진단")
        self.pg_server = ttk.Frame(nb); nb.add(self.pg_server, text="TCP 서버")
        self.pg_client = ttk.Frame(nb); nb.add(self.pg_client, text="TCP 클라이언트")
        self.pg_buf = ttk.Frame(nb); nb.add(self.pg_buf, text="버퍼/소켓")
        self.pg_draw = ttk.Frame(nb); nb.add(self.pg_draw, text="네트워크 그림판")
        self.pg_sfc = ttk.Frame(nb); nb.add(self.pg_sfc, text="Ryu SFC")
        self._build_diag()
        self._build_server()
        self._build_client()
        self._build_buf()
        self._build_draw()
        self._build_sfc()
# ---------------- 네트워크 진단 ----------------
    def _build_diag(self):
        left = ttk.Frame(self.pg_diag, padding=8); left.pack(side="left", fill="y")
        right = ttk.Frame(self.pg_diag, padding=8); right.pack(side="right", fill="both", expand=True)
        ttk.Label(left, text="IP 구성 / netstat / 포트 검사").pack(anchor="w")
        ttk.Button(left, text="IP 구성 확인", command=self.do_ipconfig).pack(fill="x", pady=2)
        self.var_netstat = tk.StringVar(value="9000")
        row = ttk.Frame(left); row.pack(fill="x", pady=2)
        ttk.Entry(row, textvariable=self.var_netstat, width=10).pack(side="left")
        ttk.Button(row, text="netstat 필터", command=self.do_netstat).pack(side="left", padx=4)
        row2 = ttk.Frame(left); row2.pack(fill="x", pady=(6,2))
        self.var_host = tk.StringVar(value="127.0.0.1")
        self.var_port = tk.StringVar(value="9000")
        ttk.Entry(row2, textvariable=self.var_host, width=14).pack(side="left")
        ttk.Entry(row2, textvariable=self.var_port, width=6).pack(side="left", padx=4)
        ttk.Button(row2, text="포트 오픈 검사", command=self.do_check_port).pack(side="left", padx=4)
        ttk.Separator(left).pack(fill="x", pady=8)
        ttk.Label(left, text="바이트/주소 변환").pack(anchor="w")
        ttk.Button(left, text="hton/ntoh 데모", command=self.do_hton).pack(fill="x", pady=2)
        self.var_ipv4 = tk.StringVar(value="8.8.8.8")
        self.var_ipv6 = tk.StringVar(value="2001:4860:4860::8888")
        row3 = ttk.Frame(left); row3.pack(fill="x", pady=2)
        ttk.Entry(row3, textvariable=self.var_ipv4, width=18).pack(side="left")
        ttk.Button(row3, text="inet_pton/ntop(IPv4)", command=self.do_inet4).pack(side="left", padx=4)
        row4 = ttk.Frame(left); row4.pack(fill="x", pady=2)
        ttk.Entry(row4, textvariable=self.var_ipv6, width=26).pack(side="left")
        ttk.Button(row4, text="inet_pton/ntop(IPv6)", command=self.do_inet6).pack(side="left", padx=4)
        ttk.Separator(left).pack(fill="x", pady=8)
        ttk.Label(left, text="DNS/이름 변환").pack(anchor="w")
        self.var_dns = tk.StringVar(value="example.com")
        self.var_rev = tk.StringVar(value="8.8.8.8")
        row5 = ttk.Frame(left); row5.pack(fill="x", pady=2)
        ttk.Entry(row5, textvariable=self.var_dns, width=18).pack(side="left")
        ttk.Button(row5, text="DNS 조회", command=self.do_dns).pack(side="left", padx=4)
        row6 = ttk.Frame(left); row6.pack(fill="x", pady=2)
        ttk.Entry(row6, textvariable=self.var_rev, width=18).pack(side="left")
        ttk.Button(row6, text="역방향 조회", command=self.do_reverse).pack(side="left", padx=4)
        self.out_diag = scrolledtext.ScrolledText(right, height=30)
        self.out_diag.pack(fill="both", expand=True)
    
    def log_diag(self, s): self._append(self.out_diag, s)

# ---- 진단 핸들러 (구현 지점) ----
    # 구현완료
    def do_ipconfig(self): #self._todo("IP 구성 확인 실행", area="diag")
        os_name = platform.system().lower()

        if "windows" in os_name:    #Window인 경우
            self.log_diag("$ ipconfig /all")
            cmd = "ipconfig /all"
        else:                       #Mac/Linux인 경우
            self.log_diag("$ ifconfig -a")
            cmd = "ifconfig -a"

        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text = True)
        self.log_diag(result.stdout)

    # 구현완료
    def do_netstat(self): #self._todo(f"netstat 필터: {self.var_netstat.get()}", area="diag")

        netstat_filter = self.var_netstat.get()
        os_name = platform.system().lower()

        cmd = "netstat -a -n -p tcp | "

        if "windows" in os_name:
            cmd += "findstr " + netstat_filter
            self.log_diag("$" + cmd + '\n')
        else:
            cmd += "grep " + netstat_filter
            self.log_diag("$" + cmd + '\n')

        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text = True)
        self.log_diag(result.stdout)

    # 구현완료 time-out 감지형태로 만들어놓음
    def do_check_port(self): #self._todo(f"포트 검사: {self.var_host.get()}:{self.var_port.get()}", area="diag")
        host = self.var_host.get()
        port = int(self.var_port.get())

        self.log_diag(f"해당 포트를 검사합니다. {host}:{port}\n")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # 임시 소켓 생성
        sock.settimeout(1)  # 1초로 설정
        try:    # 소켓 연결 시도 -> 예외 띄우면 닫혀있거나 막힌 것으로 판단
            sock.connect((host, port))
            self.log_diag(f"[Success] : Listening on {host}:{port}\n")

        except Exception as e:
            self.log_diag("[FAIL] : " + str(e) + "\n")

        finally:
            sock.close()    # 임시소켓 해제


    def do_hton(self): #self._todo("hton/ntoh 데모", area="diag")
        
        x = 12345  # 테스트용 값

        self.log_diag(f"[hton/ntoh 데모] 입력값: {x} (0x{x:04x})\n")

        # 16비트
        h2n16 = socket.htons(x)
        self.log_diag(f" [16비트] host→net = 0x{h2n16:04x}")

        # 32비트
        h2n32 = socket.htonl(x)
        self.log_diag(f" [32비트] host→net = 0x{h2n32:08x}")

        # 64비트 (struct 필요)
        net64 = struct.pack(">Q", x)     # big-endian
        self.log_diag(f" [64비트] net64 = {net64.hex()}\n")


    def do_inet4(self): #self._todo(f"inet_pton/ntop IPv4: {self.var_ipv4.get()}", area="diag")
        ipv4 = self.var_ipv4.get()
        try:
            packed = socket.inet_pton(socket.AF_INET, ipv4)
            unpacked = socket.inet_ntop(socket.AF_INET, packed)

            self.log_diag(f"[inet_pton/ntop IPv4] 입력={ipv4}\n")
            self.log_diag(f"  pton → {packed.hex()}")
            self.log_diag(f"  ntop → {unpacked}\n")

        except Exception as e:
            self.log_diag(f"[ERROR] IPv4 변환 실패: {e}\n")

    def do_inet6(self): #self._todo(f"inet_pton/ntop IPv6: {self.var_ipv6.get()}", area="diag")
        ipv6 = self.var_ipv6.get()
        try:
            packed = socket.inet_pton(socket.AF_INET6, ipv6)
            unpacked = socket.inet_ntop(socket.AF_INET6, packed)

            self.log_diag(f"[inet_pton/ntop IPv6] 입력={ipv6}\n")
            self.log_diag(f"  pton → {packed.hex()}")
            self.log_diag(f"  ntop → {unpacked}\n")

        except Exception as e:
            self.log_diag(f"[ERROR] IPv6 변환 실패: {e}\n")

    def do_dns(self): #self._todo(f"DNS 조회: {self.var_dns.get()}", area="diag")
        dn = self.var_dns.get()
        cmd = "nslookup " + dn
        self.log_diag(f"$ {cmd}\n")
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text = True)
        self.log_diag(result.stdout)


    def do_reverse(self): #self._todo(f"역방향 조회: {self.var_rev.get()}", area="diag")
        addr = self.var_rev.get()
        cmd = "nslookup " + addr
        self.log_diag(f"$ {cmd}\n")
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
        self.log_diag(result.stdout)

# ---------------- TCP 서버 ----------------
    def _build_server(self):
        top = ttk.Frame(self.pg_server, padding=8); top.pack(fill="x")
        self.var_srv_port = tk.StringVar(value="9000")
        ttk.Label(top, text="포트").pack(side="left")
        ttk.Entry(top, textvariable=self.var_srv_port, width=6).pack(side="left", padx=4)
        self.var_broadcast = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="그림판 브로드캐스트", variable=self.var_broadcast).pack(side="left", padx=6)
        ttk.Button(top, text="서버 시작", command=self.server_start).pack(side="left", padx=4)
        ttk.Button(top, text="서버 정지", command=self.server_stop).pack(side="left", padx=4)
        stat = ttk.Frame(self.pg_server, padding=8); stat.pack(fill="x")
        self.lbl_clients = ttk.Label(stat, text="접속: 0"); self.lbl_clients.pack(side="left")
        self.lbl_counter = ttk.Label(stat, text="카운터: 0"); self.lbl_counter.pack(side="left", padx=12)
        ttk.Button(stat, text="상태 갱신", command=self.server_status).pack(side="left")
        self.out_srv = scrolledtext.ScrolledText(self.pg_server, height=28)
        self.out_srv.pack(fill="both", expand=True)

    def log_srv(self, s): self._append(self.out_srv, s)


# ---- 서버 핸들러 (구현 지점) ----
    def server_start(self):
        # [구현 완료] 소켓 생성/리스닝/스레드 시작
        if self.server_running:
            return
        self.server_running = True
        self.server_stop_event.clear()

        host = "0.0.0.0"
        port = int(self.var_srv_port.get())
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((host, port))
        self.server_sock.listen()

        self.clients = [] # 접속한 클라이언트 소켓 리스트
        self.client_threads = [] # 접속한 클라이언트 스레드 리스트
        self.counter = 0

        threading.Thread(target=self.accept_loop).start()
        self.log_srv(f"[서버] 시작 @ {port}")


    def accept_loop(self):
        while not self.server_stop_event.is_set():
            try:
                client_sock, addr = self.server_sock.accept()
                self.clients.append(client_sock)

                self.log_srv(f"[접속] {addr}")

                t = threading.Thread(target=self.server_recv, args=(client_sock, addr)).start()
                self.client_threads.append(t)

            except Exception as e:
                if not self.server_stop_event.is_set():
                    self.log_srv(f"[Error] accept 실패: {e}")
                break


    def server_recv(self, client_sock, addr):
        try:
            while not self.server_stop_event.is_set():
                data = client_sock.recv(1024)
                if not data:
                    break

                # 메시지 처리
                self.log_srv(f"[수신] {addr}: {data.decode()}")

                # 공유 카운터 증가
                with self.counter_lock:
                    self.counter += 1

        except Exception as e:
            self.log_srv(f"[Error] 수신 실패 {addr}: {e}")

        finally:
            client_sock.close()
            self.clients.remove(client_sock)
            self.log_srv(f"[해제] {addr}")


    def server_stop(self):
        # [구현 완료] stop event, join
        if not self.server_running:
            return

        self.server_running = False
        self.server_stop_event.set()

        try:
            self.server_sock.close()
        except:
            pass

        # 모든 클라이언트 소켓 닫기
        for sock in self.clients:
            sock.close()

        # 모든 스레드 join하기 (안전 종료)
        for t in self.client_threads:
            t.join()

        self.log_srv("[서버] 정지 완료")


    def server_status(self):
        # TODO: 실제 접속 수/카운터 반영
        self.lbl_clients.config(text="접속: ?")
        self.lbl_counter.config(text="카운터: ?")
        self.log_srv("[서버] 상태 갱신 (스켈레톤)")


# ---------------- TCP 클라이언트 ----------------
    def _build_client(self):
        top = ttk.Frame(self.pg_client, padding=8); top.pack(fill="x")
        self.var_cli_host = tk.StringVar(value="127.0.0.1")
        self.var_cli_port = tk.StringVar(value="9000")
        ttk.Label(top, text="호스트").pack(side="left")
        ttk.Entry(top, textvariable=self.var_cli_host, width=16).pack(side="left", padx=4)
        ttk.Label(top, text="포트").pack(side="left")
        ttk.Entry(top, textvariable=self.var_cli_port, width=6).pack(side="left", padx=4)
        ttk.Button(top, text="접속", command=self.cli_connect).pack(side="left", padx=4)
        ttk.Button(top, text="해제", command=self.cli_close).pack(side="left", padx=4)
        opt = ttk.Frame(self.pg_client, padding=8); opt.pack(fill="x")
        self.var_mode = tk.StringVar(value="VAR")
        ttk.Radiobutton(opt, text="VAR(\\n)", variable=self.var_mode, value="VAR").pack(side="left")
        ttk.Radiobutton(opt, text="FIXED(32B)", variable=self.var_mode, value="FIXED").pack(side="left", padx=6)
        ttk.Radiobutton(opt, text="MIX(4B len+data)", variable=self.var_mode, value="MIX").pack(side="left", padx=6)
        self.var_after_close = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt, text="전송 후 종료", variable=self.var_after_close).pack(side="left", padx=8)
        msg = ttk.Frame(self.pg_client, padding=8); msg.pack(fill="x")
        self.var_msg = tk.StringVar(value="hello")
        ttk.Entry(msg, textvariable=self.var_msg, width=60).pack(side="left")
        ttk.Button(msg, text="전송", command=self.cli_send).pack(side="left", padx=6)
        self.out_cli = scrolledtext.ScrolledText(self.pg_client, height=28)
        self.out_cli.pack(fill="both", expand=True)
    
    def log_cli(self, s): self._append(self.out_cli, s)

# ---- 클라이언트 스켈레톤 핸들러 (구현 지점) ----
    def cli_connect(self):
        if self.client_connected:
            return

        self.client_connected = True

        host = self.var_cli_host.get()
        port = int(self.var_cli_port.get())

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((host, port))

        # --- recv 전용 스레드 시작 ---
        self.cli_stop_event = threading.Event()
        self.cli_thread = threading.Thread(target=self.cli_recv_loop, daemon=True)
        self.cli_thread.start()

        self.log_cli("[클라] 서버 연결 완료")
# TODO: socket connect + recv 루프

    def cli_recv_loop(self):
        try:
            while not self.cli_stop_event.is_set():
                data = self.client_sock.recv(1024)
                if not data:
                    break
                self.log_cli(f"[수신] {data.decode(errors='ignore')}")
        except Exception as e:
            self.log_cli(f"[클라 Error] 수신 실패: {e}")
        finally:
            self.cli_close()


    def cli_close(self):
        # [구현 완료] close
        if not self.client_connected:
            return
        
        self.client_connected = False

        try:
            if hasattr(self, 'cli_stop_event'):
                self.cli_stop_event.set()
        except:
            pass

        try:
            self.client_sock.close()
        except:
            pass

        self.log_cli("[클라] 연결 해제")


    def cli_send(self):
        # [구현 완료] VAR/FIXED/MIX 전송 구현
        if not self.client_connected:
            self.log_cli("[클라] 연결 안됨")
            return
        
        mode = self.var_mode.get()
        msg = self.var_msg.get()

        if mode == "FIXED":
            self.send_fixed(msg)
        elif mode == "VAR":
            self.send_var(msg)
        elif mode == "MIX":
            self.send_mix(msg)
        else:
            self.log_cli("[클라] 잘못된 모드")

        self.log_cli(f"[클라] ({mode}) '{msg}' 전송 완료")

        if self.var_after_close.get():
            self.log_cli("[클라] 전송 후 즉시 연결 종료 옵션 활성화 → 클라이언트 종료")
            self.cli_close()


    def send_fixed(self, msg: str):
        FIXED_LEN = 16

        b = msg.encode()

        if len(b) < FIXED_LEN:
            b = b.ljust(FIXED_LEN, b' ')   # 패딩
        else:
            b = b[:FIXED_LEN]              # 자르기

        self.client_sock.sendall(b)


    def send_var(self, msg: str):
        data = (msg + "\n").encode()
        self.client_sock.sendall(data)


    def send_mix(self, msg: str):
        payload = msg.encode()
        length = len(payload)

        prefix = length.to_bytes(4, 'big')  # 4바이트
        self.client_sock.sendall(prefix + payload)


# ---------------- 버퍼/소켓 ----------------
    def _build_buf(self):
        top = ttk.Frame(self.pg_buf, padding=8); top.pack(fill="x")
        ttk.Button(top, text="클라 소켓 버퍼 조회", command=self.buf_client).pack(side="left", padx=4)
        ttk.Button(top, text="임시 소켓 버퍼 조회", command=self.buf_temp).pack(side="left", padx=4)
        self.out_buf = scrolledtext.ScrolledText(self.pg_buf, height=30)
        self.out_buf.pack(fill="both", expand=True)

    def log_buf(self, s): self._append(self.out_buf, s)
# ---- 버퍼 스켈레톤 핸들러 ----
    def buf_client(self):
        self.log_buf("[버퍼] 클라이언트 소켓 버퍼 조회 (스켈레톤)")
# TODO: getsockopt SO_SNDBUF/SO_RCVBUF
    def buf_temp(self):
        self.log_buf("[버퍼] 임시 소켓 생성 후 버퍼 조회 (스켈레톤)")
# TODO: socket() 후 옵션 조회
# ---------------- 네트워크 그림판 ----------------
    def _build_draw(self):
        info = ttk.Frame(self.pg_draw, padding=8); info.pack(fill="x")
        ttk.Label(info, text="그림판 스켈레톤 — 드래그 시 선, (옵션) 네트워크 브로드캐스트").pack(side="left")
        self.canvas = tk.Canvas(self.pg_draw, bg="white", height=520)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas.bind("<ButtonPress-1>", self._draw_start)
        self.canvas.bind("<B1-Motion>", self._draw_move)
        self._last_xy = None
    def _draw_start(self, e): self._last_xy = (e.x, e.y)
    def _draw_move(self, e):
        if not self._last_xy: return
        x1,y1 = self._last_xy; x2,y2 = e.x, e.y
        self.canvas.create_line(x1,y1,x2,y2) # TODO: 네트워크로 동기화하려면 여기서 송신
        self._last_xy = (x2,y2)
# ---------------- Ryu SFC (REST) --------------- 
    def _build_sfc(self):
        top = ttk.Frame(self.pg_sfc, padding=8); top.pack(fill="x")
        self.var_rest_host = tk.StringVar(value="127.0.0.1")
        self.var_rest_port = tk.StringVar(value="8080")
        self.var_dpid = tk.StringVar(value="1")
        self.var_prio = tk.StringVar(value="100")
        self.var_h1 = tk.StringVar(value="1")
        self.var_fw = tk.StringVar(value="2")
        self.var_nat= tk.StringVar(value="3")
        self.var_h2 = tk.StringVar(value="4")
        
        ttk.Label(top, text="Ryu").grid(row=0, column=0, sticky="e")
        ttk.Entry(top, textvariable=self.var_rest_host, width=14).grid(row=0, column=1)
        ttk.Label(top, text=":").grid(row=0, column=2)
        ttk.Entry(top, textvariable=self.var_rest_port, width=6).grid(row=0, column=3, padx=4)
        ttk.Label(top, text="DPID").grid(row=0, column=4, sticky="e")
        ttk.Entry(top, textvariable=self.var_dpid, width=6).grid(row=0, column=5)
        ttk.Label(top, text="prio").grid(row=0, column=6, sticky="e")
        ttk.Entry(top, textvariable=self.var_prio, width=6).grid(row=0, column=7)
        
        ports = ttk.Frame(self.pg_sfc, padding=8); ports.pack(fill="x")
        
        for i,(lab,var) in enumerate([("h1",self.var_h1),("fw",self.var_fw),("nat",self.var_nat),("h2",self.var_h2)]):
            ttk.Label(ports, text=lab).grid(row=0, column=i*2)
            ttk.Entry(ports, textvariable=var, width=6).grid(row=0, column=i*2+1, padx=4)
            btns = ttk.Frame(self.pg_sfc, padding=8); btns.pack(fill="x")
            ttk.Button(btns, text="SFC 설치", command=self.sfc_install).pack(side="left", padx=4)
            ttk.Button(btns, text="바이패스", command=self.sfc_bypass).pack(side="left", padx=4)
            ttk.Button(btns, text="플로우 조회", command=self.sfc_dump).pack(side="left", padx=4)
            ttk.Button(btns, text="플로우 삭제", command=self.sfc_clear).pack(side="left", padx=4)
            self.out_sfc = scrolledtext.ScrolledText(self.pg_sfc, height=24)
            self.out_sfc.pack(fill="both", expand=True, padx=8, pady=8)

    def log_sfc(self, s): self._append(self.out_sfc, s)
# ---- SFC 스켈레톤 핸들러 ----
    def sfc_install(self): self._todo("SFC 설치 (REST POST /stats/flowentry/add)", area="sfc")
    def sfc_bypass(self): self._todo("바이패스 설치", area="sfc")
    def sfc_dump(self): self._todo("플로우 조회 (GET /stats/flow/<dpid>)", area="sfc")
    def sfc_clear(self): self._todo("플로우 삭제 (DELETE /stats/flowentry/clear/<dpid>)", area="sfc")
# ---------------- 공용 ----------------
    def _append(self, widget, text):
        widget.insert("end", text + "\n")
        widget.see("end")
    def _todo(self, msg, area):
        target = {"diag": self.out_diag, "sfc": self.out_sfc}.get(area, None)
        if target: self._append(target, f"[TODO] {msg}")
        else: messagebox.showinfo("TODO", msg)
if __name__ == "__main__":
    App().mainloop()
