import socket
import sys

hostname = 'kafka'
port = 9092

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)  # 5 second timeout

try:
    sock.connect((hostname, port))
    print(f"Successfully connected to {hostname} on port {port}")
except Exception as e:
    print(f"Failed to connect to {hostname} on port {port}: {e}")
finally:
    sock.close()
