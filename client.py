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

def download_file(server_address, port, filename):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        request = f"DOWNLOAD {filename}"
        response = send_and_receive(client_socket, request, (server_address, port))
        if response is None:
            print("No response from server")
            return

        response_parts = response.split(" ")
        if response_parts[0] == "ERR":
            print(f"Error: {response}")
            return

        file_size = int(response_parts[4])
        file_port = int(response_parts[6])
        with open(filename, "wb") as file:
            start = 0
            while start < file_size:
                end = min(start + 999, file_size - 1)
                request = f"FILE {filename} GET START {start} END {end}"
                response = send_and_receive(client_socket, request, (server_address, file_port))
                if response is None:
                    print("No response from server")
                    return

                response_parts = response.split(" ")
                if response_parts[0] == "FILE" and response_parts[1] == filename and response_parts[2] == "OK":
                    encoded_data = response_parts[8]
                    data = base64.b64decode(encoded_data)
                    file.seek(start)
                    file.write(data)
                    start = end + 1
                    print("*", end="", flush=True)
            print("\nFile download complete")

            close_request = f"FILE {filename} CLOSE"
            send_and_receive(client_socket, close_request, (server_address, file_port))

