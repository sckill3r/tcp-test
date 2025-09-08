
import struct
import globals


COMM_hostKey = 0x25
COMM_ACK = 0x33
CMD_RESTART_COMMAND = 0xE2
CMD_DEFINE_COMMAND = 0x03

def calculate_crc16_ccitt(data):
    """Calculate CRC-16-CCITT checksum for the given data."""
    crc = 0x0000
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def build_packet(command, reply_code=COMM_ACK, payload=b''):
    """Helper to build a packet with given command, reply code, and optional payload."""
    length = 5 + len(payload)
    packet = bytearray()
    packet += struct.pack('<H', length)
    packet.append(COMM_hostKey)
    packet.append(command)
    packet.append(reply_code)
    packet += payload
    crc = calculate_crc16_ccitt(packet)
    packet.append((crc >> 8) & 0xFF)
    packet.append(crc & 0xFF)
    return packet

def _receive_reply(sock):
    """Receive a reply packet from the socket."""
    try:
        sock.settimeout(5)
        header = sock.recv(2)
        if len(header) < 2:
            print("Failed to read length header.")
            return None
        length = int.from_bytes(header, 'little')
        total_size = length + 2
        data = header
        while len(data) < total_size:
            chunk = sock.recv(total_size - len(data))
            if not chunk:
                break
            data += chunk
        if len(data) < total_size:
            print("Incomplete packet received.")
            return None
        return data
    except Exception as e:
        print(f"Connection Closed")
        return None

def send_single_command(connection_log_label, log_label, command_byte):
    """Send a single command byte with COMM_ACK as reply code."""
    if not globals.client_socket_global:
        return
    packet = build_packet(command_byte)
    try:
        globals.client_socket_global.sendall(packet)

        reply = _receive_reply(globals.client_socket_global)
        if reply:
            log_label.config(text=f"Log: Reply received: {reply.hex()}")
    except Exception as e:
        connection_log_label.config(text=f"Connection Status: Waiting for connection...")

'''
def send_restart_command(log_label):
    """Send a restart command and close the connection."""
    if not globals.client_socket_global:
        log_label.config(text="No client connected.")
        return
    packet = build_packet(CMD_RESTART_COMMAND)
    try:
        globals.client_socket_global.sendall(packet)
        log_label.config(text=f"Restart command sent! Packet: {packet.hex()}")
        print("Sent:", packet.hex())
        globals.client_socket_global.close()
        print("Connection closed after restart command.")
        globals.client_socket_global = None
    except Exception as e:
        log_label.config(text=f"Connection Closed")

def send_define_command(log_label):
    """Send a define command and parse the reply."""
    if not globals.client_socket_global:
        log_label.config(text="No client connected.")
        return
    packet = build_packet(CMD_DEFINE_COMMAND)
    try:
        globals.client_socket_global.sendall(packet)
        log_label.config(text=f"Define command sent! Packet: {packet.hex()}")
        reply = _receive_reply(globals.client_socket_global)
        if reply:
            _parse_define_reply(reply, log_label)
    except Exception as e:
        log_label.config(text=f"Connection Closed")

def _parse_define_reply(data, log_label=None):
    """Parse the reply from a define command."""
    if len(data) < 7:
        if log_label:
            log_label.config(text="Reply too short.")
        return
    length = int.from_bytes(data[0:2], 'little')
    host_key = data[2]
    command = data[3]
    reply_code = data[4]
    payload = data[5:-2]
    crc_received = int.from_bytes(data[-2:], 'big')
    crc_calculated = calculate_crc16_ccitt(data[:-2])
    if crc_calculated != crc_received:
        msg = "CRC mismatch!"
        print(msg)
        if log_label:
            log_label.config(text=msg)
        return
    if len(payload) >= 10:
        fw_version_high = payload[-2]
        fw_version_low = payload[-1]
        debug_start = int.from_bytes(payload[-10:-6], 'little')
        debug_end = int.from_bytes(payload[-6:-2], 'little')
        try:
            device_info = payload[:-10].decode('ascii')
        except UnicodeDecodeError:
            device_info = payload[:-10].decode('latin1')
        print(f"FW Version: {fw_version_high}.{fw_version_low}")
        print(f"Debug Log Start: {debug_start}")
        print(f"Debug Log End: {debug_end}")
    else:
        print("Payload too short to parse version and debug info.")
    if log_label:
        log_label.config(text=f"Reply received: {data.hex()}")

def parse_define_reply(data):
    """Standalone parse for define reply (for external use)."""
    _parse_define_reply(data)

'''
