import random
import threading
import socket
import sys
import time

sockets = []

def talker_thread(conn):
  while True:
    try:
      conn.send(bytes([ord("A")] * 100_000))
    except Exception as e:
      print(f"Failed to send megabyte: {e}")
      return
    print("Sending megabyte")

def main():
  global sockets

  port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888

  s = socket.socket()
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(("0.0.0.0", port))
  s.listen(1)

  print("Socket listening on port", port)

  while True:
    conn, addr = s.accept()
    print(addr, "connected")

    threading.Thread(target=talker_thread, args=(conn, )).start()


if __name__ == "__main__":
  main()
