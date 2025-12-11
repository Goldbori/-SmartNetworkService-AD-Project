# smart_net_suite_skeleton.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import platform
import socket
import struct
import threading
import requests


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

    # ---- 진단 핸들러 ----
    def do_ipconfig(self):
        os_name = platform.system().lower()

        if "windows" in os_name:
            self.log_diag("$ ipconfig /all")
            cmd = "ipconfig /all"
        else:
            self.log_diag("$ ifconfig -a")
            cmd = "ifconfig -a"

        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
        self.log_diag(result.stdout)

    def do_netstat(self):
        netstat_filter = self.var_netstat.get()
        os_name = platform.system().lower()
        cmd = "netstat -a -n -p tcp | "

        if "windows" in os_name:
            cmd += "findstr " + netstat_filter
            self.log_diag("$" + cmd + '\n')
        else:
            cmd += "grep " + netstat_filter
            self.log_diag("$" + cmd + '\n')

        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
        self.log_diag(result.stdout)

    def do_check_port(self):
        host = self.var_host.get()
        port = int(self.var_port.get())
        self.log_diag(f"포트 검사: {host}:{port}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            sock.connect((host, port))
            self.log_diag("[Success] 포트 열려 있음.\n")
        except Exception as e:
            self.log_diag("[FAIL] " + str(e) + "\n")
        finally:
            sock.close()

    def do_hton(self):
        x = 12345
        self.log_diag(f"[hton/ntoh 데모] 입력값: {x}")
        self.log_diag(f" 16비트 htons={socket.htons(x)}")
        self.log_diag(f" 32비트 htonl={socket.htonl(x)}")

        net64 = struct.pack(">Q", x)
        self.log_diag(f" 64비트 = {net64.hex()}\n")

    def do_inet4(self):
        ipv4 = self.var_ipv4.get()
        try:
            packed = socket.inet_pton(socket.AF_INET, ipv4)
            unpacked = socket.inet_ntop(socket.AF_INET, packed)
            self.log_diag(f"입력={ipv4} → {packed.hex()} → {unpacked}\n")
        except Exception as e:
            self.log_diag("[ERROR] IPv4 변환 실패: " + str(e) + "\n")

    def do_inet6(self):
        ipv6 = self.var_ipv6.get()
        try:
            packed = socket.inet_pton(socket.AF_INET6, ipv6)
            unpacked = socket.inet_ntop(socket.AF_INET6, packed)
            self.log_diag(f"입력={ipv6} → {packed.hex()} → {unpacked}\n")
        except Exception as e:
            self.log_diag("[ERROR] IPv6 변환 실패: " + str(e) + "\n")

    def do_dns(self):
        dn = self.var_dns.get()
        cmd = "nslookup " + dn
        self.log_diag(f"$ {cmd}")
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
        self.log_diag(result.stdout)
        self.log_diag("\n")

    def do_reverse(self):
        addr = self.var_rev.get()
        cmd = "nslookup " + addr
        self.log_diag(f"$ {cmd}")
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True)
        self.log_diag(result.stdout)
        self.log_diag("\n")

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

# ---- 서버 핸들러 ----
    # 서버 실행
    def server_start(self):
        if self.server_running:
            return

        self.server_running = True
        self.server_stop_event.clear() # 서버 정지 이벤트 초기화(set되어 있으면 스레드가 종료됨)

        host = "0.0.0.0"
        port = int(self.var_srv_port.get())

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 서버 소켓 생성
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((host, port))
        self.server_sock.listen() # 리스닝 시작

        self.clients = [] # 접속한 클라이언트 소켓 정보 리스트
        self.client_threads = [] # 접속한 클라이언트 스레드 리스트
        self.counter = 0 # 클라이언트가 송신한 메시지 수(공유 카운터)

        threading.Thread(target=self.accept_loop, daemon=True).start() # 클라이언트를 accept하는 스레드 시작
        self.log_srv(f"[서버] 시작 @ {port}")

    # 서버가 정지될 때까지 클라이언트를 계속 accpet
    def accept_loop(self):
        while not self.server_stop_event.is_set():
            try:
                client_sock, addr = self.server_sock.accept()
                client_sock.settimeout(0.5)

                self.clients.append(client_sock)
                self.log_srv(f"[서버] 클라이언트 접속 → {addr}")

                # 클라이언트 수신 스레드 생성 후 실행
                t = threading.Thread(target=self.server_recv, args=(client_sock, addr), daemon=True)
                t.start()
                self.client_threads.append(t)

            except:
                break

    # 수신 메세지 처리
    def server_recv(self, client_sock, addr):
        try:
            while not self.server_stop_event.is_set():
                try:
                    mode = client_sock.recv(1)
                    if not mode:
                        break

                    # --- 그림판 브로드캐스트 모드 추가 ---
                    if mode == b'D':
                        data = self.recv_var(client_sock)
                        if data is None:
                            break
                        self.broadcast(b'D' + data, sender=client_sock)
                        self.log_srv(f"[그림] {addr} → {data.decode().strip()}")
                        continue

                    # --- 기존 메시지 모드 ---
                    if mode == b'\x01':
                        data = self.recv_fixed(client_sock)
                    elif mode == b'\x02':
                        data = self.recv_var(client_sock)
                    elif mode == b'\x03':
                        data = self.recv_mix(client_sock)
                    else:
                        self.log_srv(f"[서버] {addr} 잘못된 모드")
                        break

                    if data is None:
                        break

                    self.log_srv(f"[서버] {addr} 메시지='{data.decode()}' 수신")

                    with self.counter_lock:
                        self.counter += 1

                except socket.timeout:
                    continue

        except Exception as e:
            self.log_srv(f"[서버] 오류: {e}")

        finally:
            try:
                client_sock.close()
            except:
                pass
            if client_sock in self.clients:
                self.clients.remove(client_sock)
            self.log_srv(f"[서버] 접속 해제 → {addr}")

    # 접속한 모든 클라이언트에게 브로드캐스트
    def broadcast(self, data, sender=None):
        for cli in list(self.clients):
            if cli is not sender:
                try:
                    cli.sendall(data)
                except:
                    pass

    # 주어진 길이만큼 반복적으로 메세지 수신
    def recv_exact(self, sock, size):
        buf = b''
        while len(buf) < size and not self.server_stop_event.is_set():
            try:
                chunk = sock.recv(size - len(buf))
                if not chunk:
                    return None
                buf += chunk
            except socket.timeout:
                continue
            except:
                return None
        return buf

    # 고정 길이 수신
    def recv_fixed(self, client_sock):
        return self.recv_exact(client_sock, 32)

    # 가변 길이 수신
    def recv_var(self, client_sock):
        buf = b''
        while not self.server_stop_event.is_set():
            try:
                chunk = client_sock.recv(1)
                if not chunk:
                    return None
                buf += chunk
                if chunk == b'\n':
                    break
            except socket.timeout:
                continue
            except:
                return None
        return buf

    # 고정 + 가변 길이 수신
    def recv_mix(self, client_sock):
        length_bytes = self.recv_exact(client_sock, 4)
        if length_bytes is None:
            return None
        msg_len = int.from_bytes(length_bytes, 'big')
        return self.recv_exact(client_sock, msg_len)

    # 서버 중지
    def server_stop(self):
        if not self.server_running:
            return

        self.server_running = False
        self.server_stop_event.set()

        try:
            self.server_sock.close()
        except:
            pass

        for sock in list(self.clients):
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                sock.close()
            except:
                pass

        for t in list(self.client_threads):
            t.join(timeout=1.0)

        self.log_srv("[서버] 정지 완료")

    # 서버 실제 접속 수 및 카운터 갱신
    def server_status(self):
        self.lbl_clients.config(text=f"접속: {len(self.clients)}")
        self.lbl_counter.config(text=f"카운터: {self.counter}")
        self.log_srv("[서버] 상태 갱신")

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

# ---- 클라이언트 핸들러 (구현 지점) ----
    # 클라이언트 소켓 생성 후 서버와 연결 + 반복적으로 서버로부터 응답 수신
    def cli_connect(self):
        if self.client_connected: return
        self.client_connected = True

        host = self.var_cli_host.get()
        port = int(self.var_cli_port.get())

        # 클라이언트 소켓 생성 및 서버 접속
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((host, port))

        # 클라이언트 수신 스레드 생성 및 실행
        self.cli_stop_event = threading.Event() # 수신 스레드 종료 신호
        self.cli_thread = threading.Thread(target=self.cli_recv_loop, daemon=True)
        self.cli_thread.start()

        self.log_cli(f"[클라] 연결됨 → {host}:{port}")

    # 클라이언트 소켓이 종료될 때까지 반복적으로 서버 응답 수신
    def cli_recv_loop(self):
        try:
            while not self.cli_stop_event.is_set():
                data = self.client_sock.recv(2048)
                if not data:
                    break

                # --- 그림판 좌표 수신 처리 (client) --- [추가됨]
                if data.startswith(b'D'):
                    try:
                        coords = data[1:].decode().strip().split(',')
                        x1, y1, x2, y2 = map(int, coords)
                        self.canvas.after(0, lambda: self.canvas.create_line(x1, y1, x2, y2))
                        continue
                    except:
                        pass

                self.log_cli(f"[수신] {data.decode(errors='ignore')}")

        except Exception as e:
            self.log_cli(f"[클라 ERROR] {e}")

        finally:
            self.cli_close()

    # 클라이언트 소켓 종료
    def cli_close(self):
        if not self.client_connected:
            return
        self.client_connected = False

        try:
            self.cli_stop_event.set()
        except:
            pass

        try:
            self.client_sock.close()
        except:
            pass

        self.log_cli("[클라] 연결 해제")

    # 서버로 메세지 전송
    def cli_send(self):
        if not self.client_connected:
            self.log_cli("[클라] 연결 안됨")
            return

        mode = self.var_mode.get()
        msg = self.var_msg.get()

        # 모드별 메시지 송신
        if mode == "FIXED":
            self.send_fixed(msg)
        elif mode == "VAR":
            self.send_var(msg)
        elif mode == "MIX":
            self.send_mix(msg)

        self.log_cli(f"[전송] mode={mode}, msg='{msg}'")

        if self.var_after_close.get():
            self.cli_close()

    # 고정 길이 전송
    def send_fixed(self, msg):
        FIXED_LEN = 32
        b = msg.encode()

        if len(b) < FIXED_LEN:
            b = b.ljust(FIXED_LEN, b' ')
        else:
            b = b[:FIXED_LEN]

        self.client_sock.sendall(b'\x01' + b)

    # 가변 길이 전송
    def send_var(self, msg):
        data = (msg + "\n").encode()
        self.client_sock.sendall(b'\x02' + data)

    # 고정 + 가변 길이 전송
    def send_mix(self, msg):
        payload = msg.encode()
        length = len(payload)
        prefix = length.to_bytes(4, 'big')
        self.client_sock.sendall(b'\x03' + prefix + payload)

# ---------------- 버퍼/소켓 ----------------
    def _build_buf(self):
        top = ttk.Frame(self.pg_buf, padding=8); top.pack(fill="x")
        ttk.Button(top, text="클라 소켓 버퍼 조회", command=self.buf_client).pack(side="left", padx=4)
        ttk.Button(top, text="임시 소켓 버퍼 조회", command=self.buf_temp).pack(side="left", padx=4)
        self.out_buf = scrolledtext.ScrolledText(self.pg_buf, height=30)
        self.out_buf.pack(fill="both", expand=True)

    def log_buf(self, s): self._append(self.out_buf, s)

# ---- 버퍼 스켈레톤 핸들러 ----
    # 클라이언트 소켓 버퍼 조회
    def buf_client(self):
        self.log_buf("[버퍼] 클라이언트 소켓 버퍼 조회")

        if not hasattr(self, "client_sock") or self.client_sock is None:
            self.log_buf("[버퍼] 클라이언트 소켓 없음")
            return

        try:
            # 각 버퍼 크기 조회
            snd = self.client_sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            rcv = self.client_sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)

            self.log_buf(f"[버퍼] SO_SNDBUF (송신 버퍼): {snd} bytes")
            self.log_buf(f"[버퍼] SO_RCVBUF (수신 버퍼): {rcv} bytes")

        except Exception as e:
            self.log_buf(f"[버퍼] 조회 실패: {e}")

    # 임시 소켓 생성 후 버퍼 조회
    def buf_temp(self):
        self.log_buf("[버퍼] 임시 소켓 생성 후 버퍼 조회")

        try:
            # 임시 소켓 생성
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # 각 버퍼 크기 조회
            snd = temp_sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
            rcv = temp_sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)

            self.log_buf(f"[버퍼] SO_SNDBUF (송신 버퍼): {snd} bytes")
            self.log_buf(f"[버퍼] SO_RCVBUF (수신 버퍼): {rcv} bytes")

        except Exception as e:
            self.log_buf(f"[버퍼] 임시 소켓 조회 실패: {e}")

        finally:
            # 소켓 해제
            try:
                temp_sock.close()
            except:
                pass
# ---------------- 네트워크 그림판 ----------------
    def _build_draw(self):
        info = ttk.Frame(self.pg_draw, padding=8); info.pack(fill="x")
        ttk.Label(info, text="그림판 — 드래그 시 선, (옵션) 네트워크 브로드캐스트").pack(side="left")
        self.canvas = tk.Canvas(self.pg_draw, bg="white", height=520)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.canvas.bind("<ButtonPress-1>", self._draw_start)
        self.canvas.bind("<B1-Motion>", self._draw_move)
        self._last_xy = None
    def _draw_start(self, e): self._last_xy = (e.x, e.y)

    def _draw_move(self, e):
        if not self._last_xy: return
        x1,y1 = self._last_xy; x2,y2 = e.x, e.y

        # 로컬에 그리기
        self.canvas.create_line(x1, y1, x2, y2)

        if not self.var_broadcast.get():
            self._last_xy = (x2, y2)
            return

        # 서버 연결되어 있으면 그림 정보 전송
        if self.client_connected:
            msg = f"{x1},{y1},{x2},{y2}\n"
            try:
                self.client_sock.sendall(b'D' + msg.encode())
            except:
                pass

        self._last_xy = (x2, y2)

# ---------------- Ryu SFC ----------------
    def _build_sfc(self):
        top = ttk.Frame(self.pg_sfc, padding=8);
        top.pack(fill="x")
        self.var_rest_host = tk.StringVar(value="127.0.0.1")
        self.var_rest_port = tk.StringVar(value="8080")
        self.var_dpid = tk.StringVar(value="1")
        self.var_prio = tk.StringVar(value="100")
        self.var_h1 = tk.StringVar(value="1")
        self.var_fw = tk.StringVar(value="2")
        self.var_nat = tk.StringVar(value="3")
        self.var_h2 = tk.StringVar(value="4")

        ttk.Label(top, text="Ryu").grid(row=0, column=0, sticky="e")
        ttk.Entry(top, textvariable=self.var_rest_host, width=14).grid(row=0, column=1)
        ttk.Label(top, text=":").grid(row=0, column=2)
        ttk.Entry(top, textvariable=self.var_rest_port, width=6).grid(row=0, column=3, padx=4)
        ttk.Label(top, text="DPID").grid(row=0, column=4, sticky="e")
        ttk.Entry(top, textvariable=self.var_dpid, width=6).grid(row=0, column=5)
        ttk.Label(top, text="prio").grid(row=0, column=6, sticky="e")
        ttk.Entry(top, textvariable=self.var_prio, width=6).grid(row=0, column=7)

        ports = ttk.Frame(self.pg_sfc, padding=8);
        ports.pack(fill="x")

        for i, (lab, var) in enumerate(
                [("h1", self.var_h1), ("fw", self.var_fw), ("nat", self.var_nat), ("h2", self.var_h2)]):
            ttk.Label(ports, text=lab).grid(row=0, column=i * 2)
            ttk.Entry(ports, textvariable=var, width=6).grid(row=0, column=i * 2 + 1, padx=4)

        btns = ttk.Frame(self.pg_sfc, padding=8);
        btns.pack(fill="x")
        ttk.Button(btns, text="SFC 설치", command=self.sfc_install).pack(side="left", padx=4)
        ttk.Button(btns, text="바이패스", command=self.sfc_bypass).pack(side="left", padx=4)
        ttk.Button(btns, text="플로우 조회", command=self.sfc_dump).pack(side="left", padx=4)
        ttk.Button(btns, text="플로우 삭제", command=self.sfc_clear).pack(side="left", padx=4)

        self.out_sfc = scrolledtext.ScrolledText(self.pg_sfc, height=24)
        self.out_sfc.pack(fill="both", expand=True, padx=8, pady=8)

    def log_sfc(self, s): self._append(self.out_sfc, s)

    def _rest(self, method, url, json_data=None):
        try:
            if method == "GET":
                r = requests.get(url, timeout=2)
            elif method == "POST":
                r = requests.post(url, json=json_data, timeout=2)
            elif method == "DELETE":
                r = requests.delete(url, timeout=2)
            else:
                return None, "Unknown method"
            return r.text, None
        except Exception as e:
            return None, str(e)

    def sfc_install(self):
        host = self.var_rest_host.get()
        port = self.var_rest_port.get()
        dpid = int(self.var_dpid.get())
        prio = int(self.var_prio.get())

        h1 = int(self.var_h1.get())
        fw = int(self.var_fw.get())
        nat = int(self.var_nat.get())
        h2 = int(self.var_h2.get())

        flows = [
            {"dpid": dpid, "priority": prio, "match": {"in_port": h1}, "actions": [{"type": "OUTPUT", "port": fw}]},
            {"dpid": dpid, "priority": prio, "match": {"in_port": fw}, "actions": [{"type": "OUTPUT", "port": nat}]},
            {"dpid": dpid, "priority": prio, "match": {"in_port": nat}, "actions": [{"type": "OUTPUT", "port": h2}]}
        ]

        url = f"http://{host}:{port}/stats/flowentry/add"

        for f in flows:
            txt, err = self._rest("POST", url, f)
            if err:
                self.log_sfc("[ERROR] " + err)
                return
            self.log_sfc(f"[설치 완료] {f}")

    def sfc_bypass(self):
        host = self.var_rest_host.get()
        port = self.var_rest_port.get()
        dpid = int(self.var_dpid.get())
        prio = int(self.var_prio.get())

        h1 = int(self.var_h1.get())
        h2 = int(self.var_h2.get())

        flow = {
            "dpid": dpid,
            "priority": prio,
            "match": {"in_port": h1},
            "actions": [{"type": "OUTPUT", "port": h2}]
        }

        url = f"http://{host}:{port}/stats/flowentry/add"
        txt, err = self._rest("POST", url, flow)

        if err:
            self.log_sfc("[ERROR] " + err)
        else:
            self.log_sfc(f"[바이패스 설치 완료] {flow}")

    def sfc_dump(self):
        host = self.var_rest_host.get()
        port = self.var_rest_port.get()
        dpid = int(self.var_dpid.get())

        url = f"http://{host}:{port}/stats/flow/{dpid}"
        txt, err = self._rest("GET", url)

        if err:
            self.log_sfc("[ERROR] " + err)
        else:
            self.log_sfc(txt)

    def sfc_clear(self):
        host = self.var_rest_host.get()
        port = self.var_rest_port.get()
        dpid = self.var_dpid.get()

        url = f"http://{host}:{port}/stats/flowentry/clear/{dpid}"
        txt, err = self._rest("DELETE", url)

        if err:
            self.log_sfc("[ERROR] " + err)
        else:
            self.log_sfc(f"[플로우 삭제 완료] {dpid}")

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