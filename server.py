import socket
import threading
import os
import random
import base64

# Function to handle client requests
def handle_client_request(client_address, filename, server_socket):
    # Check if the file exists
    if not os.path.exists(filename):
        response = f"ERR {filename} NOT_FOUND"
        server_socket.sendto(response.encode(), client_address)
        return

    # Get file size
    file_size = os.path.getsize(filename)
    port = random.randint(50000, 51000)  # Random port for data transmission
    response = f"OK {filename} SIZE {file_size} PORT {port}"
    server_socket.sendto(response.encode(), client_address)

    # Create a new thread to handle file transmission
    threading.Thread(target=handle_file_transmission, args=(filename, client_address, port)).start()

