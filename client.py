import socket
import base64
import sys


def send_and_receive(sock, message, address, timeout=1, max_retries=5):
    retries = 0
    while retries < max_retries:
        sock.settimeout(timeout)
        sock.sendto(message.encode(), address)
        try:
            response, _ = sock.recvfrom(4096)
            return response.decode()
        except socket.timeout:
            print(f"Timeout occurred. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            timeout *= 2
    print("Failed to receive response after multiple retries.")
    return None
