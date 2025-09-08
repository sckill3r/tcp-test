import socket
import threading
import tkinter as tk
import globals
import commands
import sys

def start_tcp_server(host='172.16.30.94', port=9309, stop_event=None, connection_log_label=None, log_label=None):
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
                connection_log_label.config(text=f"Connection Status: Connected to {addr}")
                while True:
                    try:
                        data = client_sock.recv(1024)
                        if not data:
                            connection_log_label.config(text=f"Connection Status: Waiting for connection...")
                            print(f"Connection closed by {addr}")
                            globals.client_socket_global = None
                            break
                        log_label.config(text=f"Log: Number of bytes received: {len(data)}")
                    except (ConnectionAbortedError, OSError):
                        connection_log_label.config(text=f"Connection Status: Waiting for connection...")
                        globals.client_socket_global = None
                        break

def run_server():

    # Parse host/port from command line
    host = '172.16.30.94'
    port = 9309
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print(f"Invalid port argument: {sys.argv[2]}. Using default port {port}.")

    root = tk.Tk()
    root.title("TCP Server Control")
    tk.Label(root, text=f"TCP server is running on {host}:{port}...").pack(padx=20, pady=5)
    connection_log_label = tk.Label(root, text="Connection Status: Waiting for connection...")
    connection_log_label.pack(pady=5)
    log_label = tk.Label(root, text="Log: ")
    log_label.pack(pady=5)
    stop_event = threading.Event()
    server_thread = threading.Thread(target=start_tcp_server, kwargs={'host': host, 'port': port, 'stop_event': stop_event, 'connection_log_label': connection_log_label, 'log_label': log_label}, daemon=True)
    server_thread.start()

    

    #restart_btn = tk.Button(root, text="Send Restart Command", command=lambda: commands.send_restart_command(log_label), width=20)
    #restart_btn.pack(pady=5)

    # Add Define Command Button
    #define_btn = tk.Button(root, text="Send Define Command", command=lambda: commands.send_define_command(log_label), width=20)
    #define_btn.pack(pady=5)

    # Custom Command Section
    custom_frame = tk.Frame(root)
    custom_frame.pack(pady=5)

    tk.Label(custom_frame, text="Command Byte (hex):").grid(row=0, column=0)
    cmd_entry = tk.Entry(custom_frame, width=6)
    cmd_entry.grid(row=0, column=1)

    def send_custom_command():
        raw = cmd_entry.get().strip()
        try:
            # Parse a single hex byte from input
            command_byte = int(raw, 16)
            commands.send_single_command(connection_log_label,log_label, command_byte)
        except ValueError:
            log_label.config(text="Invalid hex input for command byte.")

    custom_btn = tk.Button(custom_frame, text="Send Custom Command", command=send_custom_command, width=20)
    custom_btn.grid(row=0, column=2, padx=5)

    def stop_server():
        stop_event.set()
        root.destroy()
        print("Server stopped.")

    tk.Button(root, text="Stop Server", command=stop_server, width=20).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    run_server()