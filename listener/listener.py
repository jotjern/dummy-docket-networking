import socket
import sys
import signal

shutdown = False

def signal_handler(signum, frame):
    global shutdown
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    shutdown = True

def main():
    global shutdown
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8888
    
    s = socket.socket()
    s.settimeout(1.0)  # Make recv() interruptible
    
    try:
        s.connect((ip, port))
        print(f"Connected to {ip}:{port}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return
    
    while not shutdown:
        try:
            data = s.recv(1_000_000)
            
            if not data:
                print("Connection closed by server")
                break
            
            print(f"Received {len(data)} bytes")
        except socket.timeout:
            continue  # Check shutdown flag
        except Exception as e:
            if not shutdown:
                print(f"Error receiving data: {e}")
            break
    
    print("Closing connection...")
    s.close()
    print("Shutdown complete")

if __name__ == "__main__":
    main()