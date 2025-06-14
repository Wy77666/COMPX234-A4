import socket
import threading
import os
import random
import base64

def handle_client_request(client_address, filename, server_socket):
    # Check if the file exists
    if not os.path.exists(filename):
        response = f"ERR {filename} NOT_FOUND"
        server_socket.sendto(response.encode(), client_address)
        return

    # Get the file size
    file_size = os.path.getsize(filename)
    port = random.randint(50000, 51000)  # Randomly select a port
    response = f"OK {filename} SIZE {file_size} PORT {port}"
    server_socket.sendto(response.encode(), client_address)

    # Create a new thread to handle file transfer
    threading.Thread(target=handle_file_transmission, args=(filename, client_address, port)).start()

def handle_file_transmission(filename, client_address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as file_socket:
        file_socket.bind(("localhost", port))
        with open(filename, "rb") as file:
            while True:
                request, _ = file_socket.recvfrom(1024)
                request_parts = request.decode().split(" ")
                if request_parts[0] == "FILE" and request_parts[1] == filename and request_parts[2] == "GET":
                    start = int(request_parts[4])
                    end = int(request_parts[6])
                    file.seek(start)
                    data = file.read(end - start + 1)
                    encoded_data = base64.b64encode(data).decode()
                    response = f"FILE {filename} OK START {start} END {end} DATA {encoded_data}"
                    file_socket.sendto(response.encode(), client_address)
                elif request_parts[0] == "FILE" and request_parts[1] == filename and request_parts[2] == "CLOSE":
                    response = f"FILE {filename} CLOSE_OK"
                    file_socket.sendto(response.encode(), client_address)
                    break

def main():
    port = 51234  # The server listens on the port
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind(("localhost", port))
        print(f"Server running on port {port}")
        while True:
            request, client_address = server_socket.recvfrom(1024)
            request_parts = request.decode().split(" ")
            if request_parts[0] == "DOWNLOAD":
                filename = request_parts[1]
                threading.Thread(target=handle_client_request, args=(client_address, filename, server_socket)).start()

if __name__ == "__main__":
    main()