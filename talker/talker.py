import random
import threading
import socket
import sys
import time
import signal

sockets = []
shutdown_event = threading.Event()
active_threads = []

def talker_thread(conn):
    while not shutdown_event.is_set():
        try:
            conn.send(bytes([ord("A")] * 100_000))
        except Exception as e:
            print(f"Failed to send megabyte: {e}")
            return
        print("Sending megabyte")
        time.sleep(0.1)  # Small delay to check shutdown_event
    
    try:
        conn.close()
    except:
        pass

def signal_handler(signum, frame):
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    shutdown_event.set()

def main():
    global sockets, active_threads

    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(1.0)  # Make accept() interruptible
    s.bind(("0.0.0.0", port))
    s.listen(1)

    print("Socket listening on port", port)

    while not shutdown_event.is_set():
        try:
            conn, addr = s.accept()
            print(addr, "connected")

            thread = threading.Thread(target=talker_thread, args=(conn,))
            thread.daemon = False
            thread.start()
            active_threads.append(thread)
        except socket.timeout:
            continue  # Check shutdown_event
        except Exception as e:
            if not shutdown_event.is_set():
                print(f"Error accepting connection: {e}")

    print("Closing server socket...")
    s.close()

    print("Waiting for active threads to finish...")
    for thread in active_threads:
        thread.join(timeout=5.0)
    
    print("Shutdown complete")

if __name__ == "__main__":
    main()