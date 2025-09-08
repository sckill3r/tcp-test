import socket
import threading
import globals
import commands
import sys
import os

def start_tcp_server(host='0.0.0.0', port=9309, stop_event=None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen()
        print(f"TCP server listening on {host}:{port}")

        server_sock.settimeout(1.0)
        while not (stop_event and stop_event.is_set()):
            try:
                client_sock, addr = server_sock.accept()
            except socket.timeout:
                continue
            with client_sock:
                globals.client_socket_global = client_sock
                print(f"Connection from {addr}")
                while True:
                    try:
                        data = client_sock.recv(1024)
                        if not data:
                            print(f"Connection closed by {addr}")
                            globals.client_socket_global = None
                            break
                        print(f"Received {len(data)} bytes from {addr}")
                    except (ConnectionAbortedError, OSError):
                        print(f"Connection aborted by {addr}")
                        globals.client_socket_global = None
                        break

def run_headless_server():
    # Parse host/port from command line
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 9309))
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port argument: {sys.argv[2]}. Using default port {port}.")

    print(f"Starting headless TCP server on {host}:{port}")
    print("Server is ready to accept connections...")
    
    stop_event = threading.Event()
    server_thread = threading.Thread(target=start_tcp_server, kwargs={'host': host, 'port': port, 'stop_event': stop_event}, daemon=True)
    server_thread.start()
    
    try:
        # Keep the main thread alive
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down server...")
        stop_event.set()

if __name__ == "__main__":
    run_headless_server()
