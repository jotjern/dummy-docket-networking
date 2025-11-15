import socket
import sys

ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888

s = socket.socket()
s.connect((ip, port))

while True:
  data = s.recv(1_000_000)

  print(f"Received {len(data)} bytes")
